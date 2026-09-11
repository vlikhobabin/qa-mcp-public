# Card 86 step 0 — element-addressing spike (findings)

Date: 2026-06-16. Reproduce: `uv run --frozen python tools/protocol-research/element_addressing_spike.py`
(capture `genuine-commit-conn` is lab-local / gitignored).

## Question

Card 86 (the keystone) hinges on ONE unknown: **how does a manager command frame address its target form
element?** If the address is a hidden numeric id or a per-element GUID, capture-free actions need a full
grammar decode. If it is the element's name/path, capture-free actions are mostly a substitution.

## Method (no new genuine runs)

In the rich genuine capture `genuine-commit-conn` (660 manager→client command frames, fixture form
`Обработка.ФикстураПротоколаTestClient`), the frames that reference **exactly one** `EditField[...]` are the
single-element-targeted commands — they cover **41 distinct fields, ~8 frames each**. Two axes:

1. **Diff two equal-length, same-TYPE single-field frames for DIFFERENT fields** → isolates the address with
   no length confound. Pair: `PF_EDIT_STRING` vs `PF_EDIT_NUMBER` (both 14-char names, same edit type), both
   the length-273 frame.
2. **Probe the bytes immediately before the element path** for several names of DIFFERENT length in the same
   group (`PF_EDIT_DATE` 12, `PF_EDIT_NUMBER` 14, `PF_EDIT_READONLY` 16) → reveals any length prefix.

## Result

**Diff (PF_EDIT_STRING@208 vs PF_EDIT_NUMBER@212, both len 273) — only 3 differing ranges:**

| offset | A | B | meaning |
|---|---|---|---|
| `[19]` | `db` | `df` | offset-19 binary message counter — **already solved** (`_set_seq`) |
| `[70..85]` | 16 bytes | 16 bytes | the per-frame nonce — **already solved** (harmless-when-stale) |
| `[252..257]` | `STRING` | `NUMBER` | the element **name** tail inside `EditField[<NAME>]` |

Nothing else differs. **There is no hidden per-element id or GUID** — the only semantic difference between
addressing two elements is the literal name in the element path.

**Path decode + length prefix** (byte before the path == its length, exactly, in all cases):

```
<0x9a><len:1><path>
path = SecondaryFrame[<sessionGUID>].ManagedForm[<formGUID>].Group[PF_GROUP_MAIN].Group[PF_GROUP_EDITS].EditField[<NAME>]
PF_EDIT_DATE     -> 0x9a a9  (len 169 == path len 169)
PF_EDIT_NUMBER   -> 0x9a ab  (len 171 == path len 171)
PF_EDIT_READONLY -> 0x9a ad  (len 173 == path len 173)
```

## Decoded addressing model

An element is addressed by a **length-prefixed, fully-qualified hierarchical path string** (latin1):
a `0x9a` string-tag, a 1-byte length, then
`SecondaryFrame[S].ManagedForm[F].Group[…].…​.EditField[NAME]`. Every component is already obtainable:

- `S` (SecondaryFrame) / `F` (ManagedForm) GUIDs — learned live in the handshake (`GuidRebinder`).
- the `Group[…]` path + the `EditField[NAME]` leaf — read live via introspection (`read_form_summary`
  already returns element names; the full path is present verbatim in the form-descriptor responses).
- the 1-byte length — recomputed when the name/path length changes (same trick `native_write` uses for the
  value's length prefix; frames are tail-marker delimited, no total-length field, so growing the path just
  grows the frame).

## Implications for card 86

- **Strategy (b) (per-element-TYPE template + live address) is nearly a straight shot**, and (a) (full
  synthesis) is now within reach: a command frame = [static per-type command structure] + [length-prefixed
  element path] + [optional length-prefixed value] + [session header (counter/nonce/msgid) + GUIDs] — all
  four understood.
- The **`ElementRef` resolver** is essentially a path builder: `(live S, live F, group-path, name) → wire
  path`, substituted into a per-type template with the 1-byte length fixup.
- The keystone unknown is **resolved from existing data** — no Vanessa re-capture needed for addressing.

## Remaining (smaller) unknowns → the per-family sub-stories

1. Confirm the SAME path addressing on the **activate / SET / click / navigate** command families (the diff
   above used the value-mode read commands; `native_write`'s SET frame also carries `EditField[...]`, so this
   is very likely identical — verify when generalizing each family).
2. Per-element-TYPE **command structure templates** (one genuine example each: edit, button, list, row,
   checkbox, date, choice) — the static bytes that distinguish the families.
3. **Element path shapes for non-EditField types** (TableBox[…].Column[…], CommandBar buttons, choice
   buttons, pages) — all readable from introspection; enumerate per type.
4. **Cross-FORM axis** (all current captures are the one fixture form): confirm the path is form-relative
   (S/F GUIDs + names) and that a real config's form descriptor yields the same path shape — covered when
   card 88 brings a real-config form.

## 86a live validation — DONE (2026-06-16)

`src/qa_mcp/protocol/element_ref.py` (`ElementRef` / `build_element_path` / `extract_element_paths` /
`retarget_element_path` / `retarget_element_leaf`) implements the path builder + length-prefixed retarget;
8 offline tests (incl. a real-capture frame) pass.

Live proof (`tools/protocol-research/{element_addressing_read_probe.py,run_addressing_read_test.sh}`, READ
side = safe): replay the `genuine-commit-conn` setup to open the form, then issue the value-read for THREE
fields by re-targeting the path leaf in a single captured PF_EDIT_STRING value-read frame — **no capture
authored for those fields**. Result on a fresh TestClient:

```
[control] PF_EDIT_STRING    value_mode=True  value='PF_EDIT_STRING_VALUE'
[addr   ] PF_EDIT_NUMBER    value_mode=True (base_mode=False) value='120,50'
[addr   ] PF_EDIT_DATE      value_mode=True (base_mode=False) value='15.01.2026 10:30:00'
[addr   ] PF_EDIT_READONLY  value_mode=True (base_mode=False) value='PF_EDIT_READONLY_VALUE'
```

Each field returned its OWN distinct live value and value-mode **flipped to exactly the field we addressed**
(`base_mode=False`). **Capture-free element addressing is proven live.** The same `retarget_element_leaf`
hook is wired into `SessionHandle.read_form_value` (a `frame_rewriter` applied post-GUID-rebind), so the
product read path addresses arbitrary fields by name — with one caveat: the value-read frames (218..221) are
not in the 8..106 template set, so making `read_form_value` itself run those live needs the value-read frames
sourced from the capture bootstrap (a small follow-up, orthogonal to addressing).

Net: the keystone unknown is not just decoded but **demonstrated live**. 86b (set+commit) applies the same
`retarget_element_leaf` to the write block; 86c (click) and 86d (navigate) reuse it per family.
