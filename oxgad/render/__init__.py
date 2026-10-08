"""OriginX Render Compiler domain."""

from oxgad import RENDER_VERSION
from oxgad.render.compiler import (
    RENDER_COMPILER_VERSION,
    RenderPlanCompilation,
    RenderPlanCompilationError,
    compile_render_plan,
    render_plan_hash,
)
from oxgad.render.first10 import (
    RENDER_FIRST10_MANIFEST_VERSION,
    build_first_10_render_manifest,
    generate_first_10_render_plans,
    write_first_10_render_manifest,
)
from oxgad.render.validator import (
    RENDER_SCHEMA_PATH,
    RenderPlanValidationError,
    is_valid_render_plan,
    load_render_schema,
    validate_render_plan,
)

__all__ = (
    "RENDER_VERSION",
    "RENDER_COMPILER_VERSION",
    "RENDER_FIRST10_MANIFEST_VERSION",
    "RENDER_SCHEMA_PATH",
    "RenderPlanCompilation",
    "RenderPlanCompilationError",
    "RenderPlanValidationError",
    "build_first_10_render_manifest",
    "compile_render_plan",
    "generate_first_10_render_plans",
    "is_valid_render_plan",
    "load_render_schema",
    "render_plan_hash",
    "validate_render_plan",
    "write_first_10_render_manifest",
)
