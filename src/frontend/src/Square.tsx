import { useState } from 'react';
import { ChromePicker } from 'react-color';

interface SquareProps {
    initialColor: {
        r: number,
        g: number;
        b: number;
    };
}

function Square(props: SquareProps) {
    const [displayColorPicker, setDisplayColorPicker] = useState(false);
    const [color, setColor] = useState(props.initialColor);

    return (
        <div>
            <div style={{
                width: '50px',
                height: '50px',
                background: `rgb(${color.r}, ${color.g}, ${color.b})`,
            }} onClick={() => {
                setDisplayColorPicker(!displayColorPicker)
            }}>
                <div style={{
                    padding: '1px',
                    cursor: 'pointer',
                }} />
            </div>
            {displayColorPicker ? <div style={{
                position: 'absolute',
                zIndex: '2',
            }}>
                <div style={{
                    position: 'fixed',
                    top: '0px',
                    right: '0px',
                    bottom: '0px',
                    left: '0px',
                }} onClick={() => {
                    setDisplayColorPicker(false);
                }} />
                <ChromePicker
                    color={color}
                    onChange={(color) => setColor(color.rgb)} />
            </div> : null}

        </div>
    )
}

export default Square