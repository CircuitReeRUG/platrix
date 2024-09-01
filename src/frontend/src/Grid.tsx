import { useState } from "react";
import Square from "./Square";

interface GridProps {
  width: number;
  height: number;
  matrix: any[];
  readyState: number;
  setPixel: (x: number, y: number, color: number) => void;
}

function Grid(props: GridProps) {
  const [, setIsColorPickerOpen] = useState(false);
  const squares: JSX.Element[] = [];

  // Create a grid of squares
  for (let i = 0; i < props.height; i++) {
    for (let j = 0; j < props.width; j++) {
      const color =
        props.matrix[i] && props.matrix[i][j]
          ? props.matrix[i][j]
          : { r: 0, g: 0, b: 0 };
      squares.push(
        <Square
          key={`p${i}:${j}`}
          x={j}
          y={i}
          initialColor={color}
          matrix={props.matrix}
          setPixel={props.setPixel}
          onColorPickerOpen={() => setIsColorPickerOpen(true)}
          onColorPickerClose={() => setIsColorPickerOpen(false)}
          readyState={props.readyState}
        />
      );
    }
  }

  // Style for the grid
  const gridStyle: React.CSSProperties = {
    display: "grid",
    gridTemplateColumns: `repeat(${props.width}, auto)`,
    gridTemplateRows: `repeat(${props.height}, auto)`,
    gap: "0",
    justifyContent: "start",
    alignItems: "start",
  };

  return <div style={gridStyle}>{squares}</div>;
}

export default Grid;
