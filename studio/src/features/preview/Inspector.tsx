import type { PreviewNode } from "../../types/studio";

type Props = {
  node: PreviewNode | null;
};

export function Inspector({ node }: Props) {
  if (!node) {
    return (
      <aside className="panel inspector" data-testid="inspector">
        <h2>Inspector</h2>
        <p className="muted">Select a node to inspect (read-only).</p>
      </aside>
    );
  }
  return (
    <aside className="panel inspector" data-testid="inspector">
      <h2>Inspector</h2>
      <dl>
        <dt>Name</dt>
        <dd>{node.name}</dd>
        <dt>ID</dt>
        <dd>{node.id}</dd>
        <dt>Type</dt>
        <dd>{node.type}</dd>
        <dt>Expected control</dt>
        <dd>{node.expectedControl ?? "—"}</dd>
        <dt>Source path</dt>
        <dd>{node.sourcePath}</dd>
        <dt>Text</dt>
        <dd>{node.text ?? "—"}</dd>
        <dt>Maturity</dt>
        <dd>{node.maturity}</dd>
        <dt>Studio validation</dt>
        <dd>unvalidated (Candidate)</dd>
      </dl>
    </aside>
  );
}
