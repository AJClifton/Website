'use client'

import React, {useState, useEffect} from "react";

const Cursor = ({blinks, blinkTime} : {blinks: number, blinkTime:number}) => {
    const [currentText, setCurrentText] = useState("|");
    const [blinkNumber, setBlinkNumber] = useState(0);

    useEffect(() => {
        if (blinkNumber <= blinks) {
            const timeout = setTimeout(() => {
                setCurrentText(() => ((blinkNumber % 2 == 0) ? "" : "|"));
                setBlinkNumber(prevBlinks => prevBlinks + 1);
            }, blinkTime);
    
            return () => clearTimeout(timeout);
        }
        else {
            setCurrentText(() => "");
        }
    }, [currentText, blinkNumber])
    
    return (<span>{currentText}</span>);
}

export default Cursor;