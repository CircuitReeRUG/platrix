import { useState } from 'react';
import { ChromePicker } from 'react-color';

interface SquareProps {
    key: string;
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
                minHeight: '12px',
            	minWidth: '12px',
                background: `rgb(${color.r}, ${color.g}, ${color.b})`,
                cursor: 'pointer',
            }} onClick={() => {
                setDisplayColorPicker(!displayColorPicker)
            }}></div>

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
                    disableAlpha={true}
                    onChangeComplete={(color) => setColor(color.rgb)} />
            </div> : null}

        </div>
    )
}

export default Square
