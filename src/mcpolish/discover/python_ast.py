"""libcst-based discoverer for Python MCP servers.

Recognises three common patterns:

1. FastMCP / Anthropic SDK decorators:
       @mcp.tool()
       @mcp.tool(name="foo", description="...")
       @server.tool()
       @app.tool()

2. Low-level Tool(...) constructor:
       Tool(name="x", description="...", inputSchema={...})

3. Imperative add_tool calls:
       server.add_tool(name="x", description="...", input_schema={...})
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

import libcst as cst
from libcst.metadata import PositionProvider

from mcpolish.discover.base import Discoverer
from mcpolish.exceptions import DiscoveryError
from mcpolish.logging import get_logger
from mcpolish.types import ParamDecl, ToolDecl

log = get_logger(__name__)

# Method names whose decorator/call we treat as a tool registration.
_TOOL_METHOD_NAMES: frozenset[str] = frozenset(
    {"tool", "add_tool"}
)
# Constructor names that build a Tool object directly.
_TOOL_CONSTRUCTOR_NAMES: frozenset[str] = frozenset({"Tool", "ToolDefinition"})
# Constructor names whose first positional arg names the MCP server itself.
_SERVER_CONSTRUCTOR_NAMES: frozenset[str] = frozenset(
    {"FastMCP", "Server", "MCPServer", "App", "FastMcp"}
)


class PythonDiscoverer:
    """Implements the `Discoverer` Protocol for Python."""

    name = "python"

    def supports(self, path: Path) -> bool:
        return path.suffix == ".py"

    def extract(self, path: Path) -> list[ToolDecl]:
        return self._parse(path).tools

    def extract_with_namespace(self, path: Path) -> tuple[list[ToolDecl], str | None]:
        """Return tools plus the first FastMCP/Server() namespace argument."""
        collector = self._parse(path)
        return collector.tools, collector.namespace

    def _parse(self, path: Path) -> "_ToolCollector":
        try:
            source = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise DiscoveryError(f"unable to read {path}: {exc}") from exc
        try:
            module = cst.parse_module(source)
        except cst.ParserSyntaxError as exc:
            raise DiscoveryError(f"syntax error in {path}: {exc}") from exc

        wrapper = cst.MetadataWrapper(module)
        visitor = _ToolCollector(file=str(path))
        wrapper.visit(visitor)
        return visitor


# ---------------------------------------------------------------------------
# CST visitor
# ---------------------------------------------------------------------------


class _ToolCollector(cst.CSTVisitor):
    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(self, file: str) -> None:
        super().__init__()
        self.file = file
        self.tools: list[ToolDecl] = []
        self.namespace: str | None = None

    # ----- FastMCP-style decorators ---------------------------------------

    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:
        for dec in node.decorators:
            call = _decorator_call(dec)
            if call is None:
                continue
            method = _attribute_method_name(call.func)
            if method not in _TOOL_METHOD_NAMES:
                continue
            self._record_function_tool(node, call)

    def _record_function_tool(self, fn: cst.FunctionDef, call: cst.Call) -> None:
        kwargs = _call_kwargs(call)
        pos = self.get_metadata(PositionProvider, fn).start

        explicit_name = _literal_str(kwargs.get("name"))
        name = explicit_name or fn.name.value
        description = _literal_str(kwargs.get("description")) or _docstring(fn) or ""

        explicit_schema = _literal_value(kwargs.get("inputSchema") or kwargs.get("input_schema"))
        if isinstance(explicit_schema, dict):
            input_schema = explicit_schema
            params = _params_from_schema(input_schema)
            schema_is_explicit = True
        else:
            params = _params_from_signature(fn)
            input_schema = _schema_from_params(params)
            schema_is_explicit = False

        decorator = _attribute_full_name(call.func)
        self.tools.append(
            ToolDecl(
                name=name,
                description=description,
                input_schema=input_schema,
                params=tuple(params),
                file=self.file,
                line=pos.line,
                col=pos.column + 1,
                decorator=decorator,
                schema_is_explicit=schema_is_explicit,
            )
        )

    # ----- Tool(...) constructor + add_tool(...) calls --------------------

    def visit_Call(self, node: cst.Call) -> None:
        func_name = _bare_name(node.func) or _attribute_method_name(node.func)
        if func_name in _TOOL_CONSTRUCTOR_NAMES or func_name == "add_tool":
            self._record_constructor_tool(node)
            return
        if func_name in _SERVER_CONSTRUCTOR_NAMES and self.namespace is None:
            self.namespace = _first_positional_str(node)

    def _record_constructor_tool(self, call: cst.Call) -> None:
        kwargs = _call_kwargs(call)
        name = _literal_str(kwargs.get("name"))
        if not name:
            return  # not actually a Tool registration
        description = _literal_str(kwargs.get("description")) or ""
        schema_val = _literal_value(
            kwargs.get("inputSchema") or kwargs.get("input_schema")
        )
        input_schema: dict[str, Any] = schema_val if isinstance(schema_val, dict) else {}
        output_val = _literal_value(
            kwargs.get("outputSchema") or kwargs.get("output_schema")
        )
        output_schema = output_val if isinstance(output_val, dict) else None
        params = _params_from_schema(input_schema)
        pos = self.get_metadata(PositionProvider, call).start
        self.tools.append(
            ToolDecl(
                name=name,
                description=description,
                input_schema=input_schema,
                output_schema=output_schema,
                params=tuple(params),
                file=self.file,
                line=pos.line,
                col=pos.column + 1,
                decorator=None,
                schema_is_explicit=True,
            )
        )


# ---------------------------------------------------------------------------
# CST helpers
# ---------------------------------------------------------------------------


def _decorator_call(dec: cst.Decorator) -> cst.Call | None:
    """Return the Call node of a decorator like @mcp.tool(...). Bare `@x` -> None."""
    decorator = dec.decorator
    if isinstance(decorator, cst.Call):
        return decorator
    return None


def _attribute_method_name(node: cst.BaseExpression) -> str | None:
    """`mcp.tool` -> "tool". `mcp.foo.tool` -> "tool". Plain `x` -> None."""
    if isinstance(node, cst.Attribute):
        return node.attr.value
    return None


def _attribute_full_name(node: cst.BaseExpression) -> str | None:
    if isinstance(node, cst.Attribute):
        prefix = _attribute_full_name(node.value) or _bare_name(node.value)
        if prefix is None:
            return node.attr.value
        return f"{prefix}.{node.attr.value}"
    return _bare_name(node)


def _bare_name(node: cst.BaseExpression) -> str | None:
    if isinstance(node, cst.Name):
        return node.value
    return None


def _call_kwargs(call: cst.Call) -> dict[str, cst.BaseExpression]:
    out: dict[str, cst.BaseExpression] = {}
    for arg in call.args:
        if arg.keyword is not None:
            out[arg.keyword.value] = arg.value
    return out


def _first_positional_str(call: cst.Call) -> str | None:
    for arg in call.args:
        if arg.keyword is not None:
            continue
        return _literal_str(arg.value)
    return None


def _literal_str(node: cst.BaseExpression | None) -> str | None:
    if node is None:
        return None
    if isinstance(node, cst.SimpleString):
        try:
            return ast.literal_eval(node.value)  # safely unwraps quoting
        except (ValueError, SyntaxError):
            return None
    if isinstance(node, cst.ConcatenatedString):
        try:
            return ast.literal_eval(node.evaluated_value or "")
        except Exception:  # noqa: BLE001
            return None
    return None


def _literal_value(node: cst.BaseExpression | None) -> Any:
    """Evaluate a Python literal expression. Returns None if not a literal."""
    if node is None:
        return None
    try:
        code = cst.Module(body=[]).code_for_node(node)
        return ast.literal_eval(code)
    except (ValueError, SyntaxError):
        return None


def _docstring(fn: cst.FunctionDef) -> str | None:
    body = fn.body
    if not isinstance(body, cst.IndentedBlock) or not body.body:
        return None
    first = body.body[0]
    if isinstance(first, cst.SimpleStatementLine) and first.body:
        stmt = first.body[0]
        if isinstance(stmt, cst.Expr) and isinstance(
            stmt.value, (cst.SimpleString, cst.ConcatenatedString)
        ):
            try:
                code = cst.Module(body=[]).code_for_node(stmt.value)
                value = ast.literal_eval(code)
                if isinstance(value, str):
                    return value.strip()
            except (ValueError, SyntaxError):
                return None
    return None


# ---------------------------------------------------------------------------
# Param extraction
# ---------------------------------------------------------------------------


def _params_from_signature(fn: cst.FunctionDef) -> list[ParamDecl]:
    """Pull (name, type, required) from a function signature.

    Description for each param is heuristically pulled from the docstring's
    `Args:` / `Parameters:` block when present.
    """
    params: list[ParamDecl] = []
    doc = _docstring(fn) or ""
    descriptions = _parse_arg_block(doc)
    for p in fn.params.params:
        name = p.name.value
        if name in {"self", "cls", "ctx", "context"}:
            continue
        type_str = _annotation_str(p.annotation)
        json_type = _python_type_to_json_type(type_str) if type_str else None
        required = p.default is None
        param_desc = descriptions.get(name)
        params.append(
            ParamDecl(
                name=name,
                type=json_type,
                description=param_desc,
                required=required,
                has_example=bool(param_desc and "example" in param_desc.lower()),
            )
        )
    return params


def _annotation_str(annotation: cst.Annotation | None) -> str | None:
    if annotation is None:
        return None
    try:
        return cst.Module(body=[]).code_for_node(annotation.annotation).strip()
    except Exception:  # noqa: BLE001
        return None


def _parse_arg_block(docstring: str) -> dict[str, str]:
    """Recognise simple `Args:` / `Parameters:` blocks.

    name: description
    name (type): description
    """
    out: dict[str, str] = {}
    if not docstring:
        return out
    lines = docstring.splitlines()
    in_block = False
    current_name: str | None = None
    current_buf: list[str] = []
    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()
        lower = stripped.lower().rstrip(":")
        if lower in {"args", "arguments", "parameters", "params"}:
            in_block = True
            continue
        if in_block and not stripped:
            if current_name and current_buf:
                out[current_name] = " ".join(current_buf).strip()
            current_name = None
            current_buf = []
            in_block = False
            continue
        if not in_block:
            continue
        if ":" in stripped and not stripped.startswith(("-", "*")):
            head, _, tail = stripped.partition(":")
            head = head.strip()
            head_name = head.split("(")[0].strip()
            if head_name and not head_name.startswith(" "):
                if current_name and current_buf:
                    out[current_name] = " ".join(current_buf).strip()
                current_name = head_name
                current_buf = [tail.strip()] if tail.strip() else []
                continue
        if current_name is not None:
            current_buf.append(stripped)
    if current_name and current_buf:
        out[current_name] = " ".join(current_buf).strip()
    return out


def _params_from_schema(schema: dict[str, Any]) -> list[ParamDecl]:
    if not isinstance(schema, dict):
        return []
    props = schema.get("properties", {})
    required = set(schema.get("required", []))
    out: list[ParamDecl] = []
    if not isinstance(props, dict):
        return out
    for name, body in props.items():
        if not isinstance(body, dict):
            continue
        out.append(
            ParamDecl(
                name=name,
                type=body.get("type"),
                description=body.get("description"),
                required=name in required,
                has_example="example" in body or "examples" in body,
                raw=body,
            )
        )
    return out


def _schema_from_params(params: list[ParamDecl]) -> dict[str, Any]:
    if not params:
        return {"type": "object", "properties": {}}
    props: dict[str, Any] = {}
    required: list[str] = []
    for p in params:
        entry: dict[str, Any] = {}
        if p.type:
            entry["type"] = _python_type_to_json_type(p.type)
        if p.description:
            entry["description"] = p.description
        props[p.name] = entry
        if p.required:
            required.append(p.name)
    schema: dict[str, Any] = {"type": "object", "properties": props}
    if required:
        schema["required"] = required
    return schema


_PY_TO_JSON: dict[str, str] = {
    "str": "string",
    "int": "integer",
    "float": "number",
    "bool": "boolean",
    "bytes": "string",
    "list": "array",
    "dict": "object",
    "None": "null",
}


def _python_type_to_json_type(py_type: str) -> str:
    head = py_type.split("[")[0].strip()
    return _PY_TO_JSON.get(head, "string")
