import { RequesterSwitch } from "./RequesterSwitch";

type HeaderProps = {
  requesterId: string;
  onRequesterChange: (id: string) => void;
};

/**
 * App-level header
 *
 * Left: "Recruiting Chat" title (mirrors <h2> in .chat-header of the mockup).
 * Right: RequesterSwitch (dropdown + active badge).
 *
 * Styled via .app-header / .app-header__title in styles.css.
 */
export function Header({ requesterId, onRequesterChange }: HeaderProps) {
  return (
    <header className="app-header">
      <h1 className="app-header__title">Recruiting Chat</h1>

      <RequesterSwitch value={requesterId} onChange={onRequesterChange} />
    </header>
  );
}
