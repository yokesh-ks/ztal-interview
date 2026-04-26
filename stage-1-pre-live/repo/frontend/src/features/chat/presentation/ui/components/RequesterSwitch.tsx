import { CHAT_REQUESTERS } from "../../constants/chatExperience";

type RequesterSwitchProps = {
  value: string;
  onChange: (id: string) => void;
};

/**
 * Requester Switch
 *
 * Renders a labelled pill-shaped <select> showing all available requesters
 * plus an accent badge reflecting the currently active requester — mirrors
 * the `.status` + `#requester` pattern in chat_mockup.html.
 */
export function RequesterSwitch({ value, onChange }: RequesterSwitchProps) {
  const active = CHAT_REQUESTERS.find((r) => r.id === value);

  return (
    <div className="requester-switch">
      <span className="requester-switch__label">Requester</span>

      <select
        id="requester-select"
        className="requester-switch__select"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        aria-label="Select active requester"
      >
        {CHAT_REQUESTERS.map((r) => (
          <option key={r.id} value={r.id}>
            {r.id} – {r.label}
          </option>
        ))}
      </select>

      {active && (
        <span className="requester-switch__badge" aria-live="polite">
          {active.id}
        </span>
      )}
    </div>
  );
}
