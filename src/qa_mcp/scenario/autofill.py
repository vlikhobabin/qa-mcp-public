"""Card 106 change 4 (write side) — metadata-driven required-field autofill for create-form smoke.

Vanessa needs you to hand-author every field fill. qa-mcp can READ a 1C object's metadata, find the MANDATORY
attributes (the ones the platform would refuse to save empty), and synthesize a smoke value per type — so a
create-form smoke can open the form, fill what's required, and attempt a save, with NO hand-authoring. A genuine
"beyond Vanessa" capability.

Pure functions over the EDT `.mdo` XML (namespace-agnostic by local tag name), so fully unit-testable offline:
an attribute is REQUIRED iff it carries ``<fillChecking>ShowError</fillChecking>`` (the EDT form of
«ЗаполнениеПроверки = ВыдаватьОшибку»). Custom attributes (`<attributes>`) carry their own Russian name + a
``<type><types>…</types></type>``; standard attributes (`<standardAttributes>`, e.g. Description/Code/Date) carry
an English name mapped here to the Russian form field + an implicit type. Reference-typed required fields
(CatalogRef./DocumentRef./EnumRef./…) cannot be auto-valued without an existing ref, so they are reported but
marked ``fillable=False`` (the smoke fills primitives; refs are a documented gap).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from xml.etree import ElementTree as ET

# EDT standard-attribute English name -> (Russian form-field name, synthetic type token). Standard attributes have
# no explicit <type> in the mdo; their type is implicit. Owner/Parent are references (not auto-fillable).
_STANDARD = {
    "Description": ("Наименование", "String"),
    "Code": ("Код", "String"),
    "Date": ("Дата", "Date"),
    "Number": ("Номер", "String"),
    "Owner": ("Владелец", "Ref"),
    "Parent": ("Родитель", "Ref"),
    "Posted": ("Проведен", "Boolean"),
}

# a primitive 1C/EDT type token -> a deterministic smoke value (no Date.now: dates are fixed). Reference tokens
# (anything ending in "Ref" or containing ".") return None — not auto-fillable.
_PRIMITIVE_VALUE = {
    "String": "QASMOKE",
    "Number": "1",
    "Date": "01.01.2030",
    "Boolean": "Истина",
    "DateTime": "01.01.2030",
}


@dataclass(frozen=True)
class RequiredField:
    name: str          # the Russian form-field name (custom name as-is; standard mapped)
    type: str          # the type token (String / Number / Date / Boolean / CatalogRef.X / …)
    value: str | None  # a synthesized smoke value, or None when not auto-fillable (references)
    standard: bool     # True for a standard attribute (Наименование/Код/Дата/…), False for a custom one

    @property
    def fillable(self) -> bool:
        return self.value is not None


def _local(tag: str) -> str:
    """Strip an XML namespace: '{ns}attributes' -> 'attributes'."""
    return tag.rsplit("}", 1)[-1]


def smoke_value_for_type(type_token: str) -> str | None:
    """A deterministic smoke value for a primitive type token, or None for a reference / unknown type."""
    token = (type_token or "").strip()
    if token in _PRIMITIVE_VALUE:
        return _PRIMITIVE_VALUE[token]
    return None  # references (CatalogRef.X / DocumentRef.X / EnumRef.X / AnyRef / …) need an existing ref


# a reference type token's metadata kind -> the standard-OData entity-set prefix (the existing-value source).
# Enums are NOT OData entity sets (their values are metadata), so EnumRef is not resolved here.
_REF_ENTITY_PREFIX = {"CatalogRef": "Catalog_", "DocumentRef": "Document_",
                      "ChartOfCharacteristicTypesRef": "ChartOfCharacteristicTypes_"}
# presentation fields to try, in order, for an existing reference value (catalogs → Description; documents → Number)
_PRESENTATION_FIELDS = ("Description", "Number", "Code")


def reference_entity_set(type_token: str) -> str | None:
    """Map a reference type token to its standard-OData entity set: ``CatalogRef.Контрагенты`` → ``Catalog_Контрагенты``,
    ``DocumentRef.Заказ`` → ``Document_Заказ``. Returns None for non-references and EnumRef (enums aren't OData sets)."""
    token = (type_token or "").strip()
    if "." not in token:
        return None
    kind, _, name = token.partition(".")
    prefix = _REF_ENTITY_PREFIX.get(kind)
    return f"{prefix}{name}" if (prefix and name) else None


def resolve_reference_value(type_token: str, odata_client: Any) -> str | None:
    """For a reference-typed required field, pick an EXISTING value from the data layer (read-only OData): fetch the
    first record of the referenced entity set and return its presentation (Description / Number / Code). Returns
    None for non-references, EnumRef, an empty set, or an OData error. ``odata_client`` is a ``qa_mcp.data.ODataClient``
    (injectable fetcher → offline-testable)."""
    entity_set = reference_entity_set(type_token)
    if entity_set is None or odata_client is None:
        return None
    try:
        records = odata_client.query(entity_set, top=1)  # full first record (no $select → works for any set)
    except Exception:  # noqa: BLE001 — a missing set / HTTP error just means "can't auto-value this ref"
        return None
    if not records:
        return None
    record = records[0]
    for field in _PRESENTATION_FIELDS:
        value = record.get(field)
        if value not in (None, ""):
            return str(value)
    return None


def _field_type(block: ET.Element, name_en: str, standard: bool) -> str:
    if standard:
        return _STANDARD.get(name_en, (name_en, "String"))[1]
    # custom attribute: <type><types>String</types></type> (may carry multiple <types>; take the first)
    for child in block:
        if _local(child.tag) == "type":
            for t in child:
                if _local(t.tag) == "types" and (t.text or "").strip():
                    return t.text.strip()
    return "String"


def _root_child_text(root: ET.Element, local_name: str) -> str | None:
    return next((c.text for c in root if _local(c.tag) == local_name and (c.text or "").strip()), None)


def required_fields_from_mdo(mdo_xml: str) -> list[RequiredField]:
    """Parse an EDT object `.mdo`, returning its MANDATORY fields (fillChecking=ShowError) with synthesized smoke
    values. Standard attributes are mapped to their Russian form-field name; custom attributes keep their name.

    The EDT default puts fillChecking=ShowError on the standard Owner/Parent regardless, so those are only kept
    when the object actually has them: Owner iff the object declares ``<owners>`` (is subordinate); Parent iff it
    declares ``<hierarchical>true</hierarchical>``."""
    root = ET.fromstring(mdo_xml)
    has_owner = _root_child_text(root, "owners") is not None
    is_hier = (_root_child_text(root, "hierarchical") or "").strip().lower() == "true"
    out: list[RequiredField] = []
    for block in root:
        tag = _local(block.tag)
        if tag not in ("standardAttributes", "attributes"):
            continue
        standard = tag == "standardAttributes"
        name_en = next((c.text for c in block if _local(c.tag) == "name" and c.text), None)
        required = any(_local(c.tag) == "fillChecking" and (c.text or "").strip() == "ShowError" for c in block)
        if not name_en or not required:
            continue
        if standard and name_en == "Owner" and not has_owner:
            continue  # non-subordinate catalog: Owner is vacuous despite the EDT-default fillChecking
        if standard and name_en == "Parent" and not is_hier:
            continue  # non-hierarchical catalog: Parent is vacuous
        type_token = _field_type(block, name_en, standard)
        field_name = _STANDARD.get(name_en, (name_en, ""))[0] if standard else name_en
        # a reference (e.g. CatalogRef.Контрагенты) is not auto-valued; Owner/Parent map to "Ref"
        value = smoke_value_for_type(type_token)
        out.append(RequiredField(name=field_name, type=type_token, value=value, standard=standard))
    return out


def enum_values_from_mdo(enum_mdo_xml: str) -> list[dict[str, str | None]]:
    """Parse an Enum `.mdo`, returning its values in declaration order as ``{name, synonym}`` (synonym = the ru
    presentation). The first value is the natural autofill choice for a required EnumRef field."""
    root = ET.fromstring(enum_mdo_xml)
    out: list[dict[str, str | None]] = []
    for block in root:
        if _local(block.tag) != "enumValues":
            continue
        name = next((c.text for c in block if _local(c.tag) == "name" and c.text), None)
        synonym: str | None = None
        for c in block:
            if _local(c.tag) == "synonym":
                synonym = next((g.text for g in c if _local(g.tag) == "value" and g.text), None)
                break
        if name:
            out.append({"name": name, "synonym": synonym})
    return out


def resolve_enum_value(type_token: str, enum_mdo_provider: Any) -> str | None:
    """For a required ``EnumRef.<Имя>`` field, return the first enum value's presentation (synonym, else name).
    ``enum_mdo_provider(enum_name)`` returns the enum's `.mdo` XML (or None) — enums aren't OData sets, so their
    values come from metadata. Returns None for a non-enum, a missing provider/enum, or an empty enum."""
    token = (type_token or "").strip()
    if not token.startswith("EnumRef.") or enum_mdo_provider is None:
        return None
    enum_name = token.partition(".")[2]
    mdo = enum_mdo_provider(enum_name)
    if not mdo:
        return None
    values = enum_values_from_mdo(mdo)
    if not values:
        return None
    return values[0]["synonym"] or values[0]["name"]


def build_autofill_plan(mdo_xml: str, kind: str, name: str, *, odata_client: Any = None,
                        enum_mdo_provider: Any = None) -> dict[str, Any]:
    """Build a create-and-fill plan for an object from its `.mdo`: the create-form nav-link, the required fields
    (with values), and which are auto-fillable. ``kind`` is "Справочник" or "Документ" (EDT/ru). Primitives get a
    synthesized value; when ``odata_client`` is given, reference-typed required fields (CatalogRef./DocumentRef.)
    are resolved to an EXISTING value from the data layer — so the plan covers documents, not just primitive
    catalogs (the autofill follow-on). When ``enum_mdo_provider`` is given, required EnumRef fields take the first
    enum value (synonym) from the enum's `.mdo`. Each required entry carries ``source``: "synthesized" | "odata-ref"
    | "enum" | None."""
    required: list[dict[str, Any]] = []
    for f in required_fields_from_mdo(mdo_xml):
        value, source = f.value, ("synthesized" if f.value is not None else None)
        if value is None and odata_client is not None and reference_entity_set(f.type):
            resolved = resolve_reference_value(f.type, odata_client)
            if resolved is not None:
                value, source = resolved, "odata-ref"
        if value is None and enum_mdo_provider is not None and f.type.startswith("EnumRef."):
            resolved = resolve_enum_value(f.type, enum_mdo_provider)
            if resolved is not None:
                value, source = resolved, "enum"
        required.append({"name": f.name, "type": f.type, "value": value, "fillable": value is not None,
                         "standard": f.standard, "source": source})
    return {
        "object": f"{kind}.{name}",
        "create_link": f"e1cib/data/{kind}.{name}",
        "required": required,
        "fillable": [{"name": r["name"], "value": r["value"], "source": r["source"]} for r in required if r["fillable"]],
        "unfillable": [{"name": r["name"], "type": r["type"]} for r in required if not r["fillable"]],
    }


def _field_name_value(f: Any) -> "tuple[str, Any]":
    """Accept a RequiredField or a plan dict ({name, value}); return (name, value)."""
    if isinstance(f, dict):
        return f.get("name", ""), f.get("value")
    return f.name, f.value


def create_fill_feature(kind_phrase: str, name: str, fillable: "list[Any]",
                        feature_name: str = "smoke — создание с автозаполнением") -> str:
    """Render a runnable create-and-fill `.feature` using only canonical steps: «я создаю новый <kind> 'X'» +
    one «в поле 'F' я ввожу текст 'V'» per field with a value. ``kind_phrase`` is the create-step object phrase
    ("документ" | "элемент справочника"); ``fillable`` is a list of RequiredField OR plan dicts ({name, value}) —
    entries with a non-None value (synthesized primitives AND odata-resolved references) become input steps."""
    lines = ["# language: ru", f"Функционал: {feature_name}", f"  Сценарий: {kind_phrase} {name}",
             f"    Когда я создаю новый {kind_phrase} '{name}'"]
    for f in fillable:
        nm, val = _field_name_value(f)
        if val is not None:
            lines.append(f"    И в поле с именем '{nm}' я ввожу текст '{val}'")
    return "\n".join(lines) + "\n"
