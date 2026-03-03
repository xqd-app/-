import React from 'react';

const Controls: React.FC = () => {
    const handleZoomIn = () => {
        // Implement zoom in functionality
    };

    const handleZoomOut = () => {
        // Implement zoom out functionality
    };

    const handleReset = () => {
        // Implement reset functionality
    };

    return (
        <div className="controls">
            <button onClick={handleZoomIn}>Zoom In</button>
            <button onClick={handleZoomOut}>Zoom Out</button>
            <button onClick={handleReset}>Reset</button>
        </div>
    );
};

export default Controls;