interface HeaderProps {
  title: string;
  count: number;
}

function Header({ title, count }: HeaderProps) {
  return (
    <header className="header">
      <h1>{title}</h1>
      <p>{count} encounter(s) loaded</p>
    </header>
  );
}

export default Header;
