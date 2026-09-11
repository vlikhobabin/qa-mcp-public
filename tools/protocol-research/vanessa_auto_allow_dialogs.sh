#!/usr/bin/env bash
# Autonomously click [Да] on 1C «Предупреждение безопасности» modal dialogs (the
# external-.epf / ЗапуститьПриложение / HTML trust prompts that DisableUnsafeActionProtection
# does NOT suppress for an external Vanessa .epf). [Да] = (right-133, bottom-27) of the modal.
DISP="${1:-:77}"
DUR="${2:-150}"
END=$((SECONDS+DUR))
clicks=0
while [ "$SECONDS" -lt "$END" ]; do
  DLG=$(DISPLAY="$DISP" xdotool search --name "^1С:Предприятие$" 2>/dev/null | tail -1)
  if [ -n "$DLG" ]; then
    geom=$(DISPLAY="$DISP" xdotool getwindowgeometry --shell "$DLG" 2>/dev/null)
    eval "$geom"
    if [ -n "${WIDTH:-}" ] && [ "${WIDTH:-0}" -gt 100 ]; then
      cy=$((Y + HEIGHT - 27))
      # [Да] of a Да/Нет dialog is at right-133; [OK] of an OK-only dialog (e.g. "Отсутствует
      # редактор Vanessa Automation Editor") is at right-55. Click both: on a Да/Нет dialog the
      # [Да] click dismisses it (the OK-position click then lands harmlessly on the form); on an
      # OK-only dialog the [OK] click dismisses it.
      DISPLAY="$DISP" xdotool mousemove $((X + WIDTH - 133)) "$cy" click 1 2>/dev/null
      DISPLAY="$DISP" xdotool mousemove $((X + WIDTH - 55)) "$cy" click 1 2>/dev/null
      clicks=$((clicks+1))
      echo "click#$clicks [Да|OK] dlg=$DLG geom=${WIDTH}x${HEIGHT}+${X}+${Y}"
    fi
  fi
  sleep 0.7
done
echo "done clicks=$clicks"
