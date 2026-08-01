import type { PreviewNode } from "../../types/studio";

type Props = {
  root: PreviewNode | null;
  selectedId: string | null;
  onSelect: (node: PreviewNode) => void;
};

function TreeRows({
  node,
  depth,
  selectedId,
  onSelect,
}: {
  node: PreviewNode;
  depth: number;
  selectedId: string | null;
  onSelect: (node: PreviewNode) => void;
}) {
  return (
    <>
      <button
        type="button"
        className={`tree-item ${selectedId === node.id ? "active" : ""}`}
        style={{ paddingLeft: 14 + depth * 12 }}
        onClick={() => onSelect(node)}
      >
        {node.type === "unsupported-placeholder" ? "⚠ " : ""}
        {node.name}
      </button>
      {node.children.map((child) => (
        <TreeRows
          key={child.id}
          node={child}
          depth={depth + 1}
          selectedId={selectedId}
          onSelect={onSelect}
        />
      ))}
    </>
  );
}

export function ScreenTree({ root, selectedId, onSelect }: Props) {
  return (
    <div data-testid="screen-tree">
      <h2>Control tree</h2>
      {root ? (
        <TreeRows node={root} depth={0} selectedId={selectedId} onSelect={onSelect} />
      ) : (
        <p className="muted">No screen selected</p>
      )}
    </div>
  );
}
