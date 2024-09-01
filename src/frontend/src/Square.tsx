import { useState, useEffect } from "react";
import "./Square.css";

interface SquareProps {
  key: string;
  x: number;
  y: number;
  initialColor: {
    r: number;
    g: number;
    b: number;
  };
  matrix: any[];
  setPixel: (x: number, y: number, color: number) => void;
  onColorPickerOpen: () => void;
  onColorPickerClose: () => void;
}

function Square(props: SquareProps) {
  const [color, setColor] = useState(props.initialColor);

  const unpackColor = (packedColor: number) => {
    const r = (packedColor >> 8) & 0xF8;
    const g = (packedColor >> 3) & 0xFC;
    const b = (packedColor << 3) & 0xF8;
    return { r, g, b };
  };

  const packColor = (r: number, g: number, b: number) => {
    return ((r & 0xf8) << 8) | ((g & 0xfc) << 3) | (b >> 3);
  };

  const rgbToHex = (r: number, g: number, b: number) => {
    return (
      "#" +
      ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1).toUpperCase()
    );
  };

  const hexToRgb = (hex: string) => {
    const bigint = parseInt(hex.slice(1), 16);
    return {
      r: (bigint >> 16) & 255,
      g: (bigint >> 8) & 255,
      b: bigint & 255,
    };
  };

  // If matrix changes, check if the color of this square has changed
  useEffect(() => {
    const packedColor = props.matrix[props.y] && props.matrix[props.y][props.x];
    if (packedColor != null) {
      const newColor = unpackColor(packedColor);
      if (
        newColor.r !== color.r ||
        newColor.g !== color.g ||
        newColor.b !== color.b
      ) {
        console.log(`Updating color of square at (${props.x}, ${props.y}) from matrix data.`); // DEBUG!
        setColor(newColor);
      }
    }
  }, [props.matrix, props.x, props.y]);

  // Function to handle color change
  const handleColorChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newColor = hexToRgb(event.target.value);
    setColor(newColor);
    const packedColor = packColor(newColor.r, newColor.g, newColor.b); // DEBUG!
    console.log(`Setting pixel at (${props.x}, ${props.y}) to color: ${packedColor}`);
    props.setPixel(props.x, props.y, packedColor);
  };

  const squareStyle: React.CSSProperties = {
    backgroundColor: rgbToHex(color.r, color.g, color.b),
  };

  return (
    <div
      className="pixel"
      style={squareStyle}
      onClick={() => {
        document.getElementById(`input-${props.x}-${props.y}`)?.click();
      }}
    >
      {/* Hidden color input */}
      <input
        id={`input-${props.x}-${props.y}`}
        type="color"
        value={rgbToHex(color.r, color.g, color.b)}
        onFocus={props.onColorPickerOpen}
        onChange={handleColorChange}
        onBlur={props.onColorPickerClose}
      />
    </div>
  );
}

export default Square;
