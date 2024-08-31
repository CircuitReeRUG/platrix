import Square from './Square';

interface GridProps {
    width: number,
    height: number,
}

function Grid(props: GridProps) {

    const squares = [];

    const generateRandomColor = () => {
        return {
            r: Math.random() * 255,
            g: Math.random() * 255,
            b: Math.random() * 255,
        };
    };

    for (let i = 0; i < props.height; i++) {
        for (let j = 0; j < props.width; j++) {
            squares.push(<Square
                key={`p${i}:${j}`}
                initialColor={generateRandomColor()}
            />)
        }
    }

    const gridStyle = {
        display: 'grid',
        gridTemplateColumns: `repeat(${props.width}, 1fr)`,
    };

    return (
        <div id="pixelGrid" style={gridStyle}>
            {squares}
        </div>
    )
}

export default Grid;
