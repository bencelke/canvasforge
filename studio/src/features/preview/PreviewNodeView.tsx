import type { CSSProperties } from "react";
import type { PreviewNode } from "../../types/studio";

type Props = {
  node: PreviewNode;
  selectedId: string | null;
  onSelect: (node: PreviewNode) => void;
};

export function PreviewNodeView({ node, selectedId, onSelect }: Props) {
  const style: CSSProperties = {
    background: node.styles.fill ?? undefined,
    color: node.styles.color ?? undefined,
    fontSize: node.styles.fontSize ?? undefined,
    fontWeight: node.styles.fontWeight ?? undefined,
    padding: node.styles.padding ?? undefined,
    gap: node.styles.gap ?? undefined,
    border: selectedId === node.id ? "2px solid #0f766e" : (node.styles.border ?? undefined),
    borderRadius: node.styles.borderRadius ?? undefined,
    display: "flex",
    flexDirection: node.styles.flexDirection ?? "column",
    alignItems: node.styles.alignItems ?? undefined,
    justifyContent: node.styles.justifyContent ?? undefined,
    width: "100%",
    minHeight: node.type === "screen" ? 420 : undefined,
    cursor: "pointer",
  };

  return (
    <div
      className={`preview-node ${node.type}`}
      style={style}
      role="treeitem"
      tabIndex={0}
      aria-label={node.accessibility.label || node.name}
      data-testid={`preview-node-${node.type}`}
      onClick={(event) => {
        event.stopPropagation();
        onSelect(node);
      }}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          onSelect(node);
        }
      }}
    >
      {node.text ? <div>{node.text}</div> : null}
      {node.children.map((child) => (
        <PreviewNodeView
          key={child.id}
          node={child}
          selectedId={selectedId}
          onSelect={onSelect}
        />
      ))}
    </div>
  );
}
