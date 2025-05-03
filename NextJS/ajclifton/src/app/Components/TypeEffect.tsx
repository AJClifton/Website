'use client'

import React, {useState, useEffect} from "react";


const TypeEffect = ({text, delay, startingIndex, initialDelay}: {text: string, delay: number, startingIndex: number, initialDelay: number}) => {
    const [currentIndex, setCurrentIndex] = useState(startingIndex);
    const [currentText, setCurrentText] = useState(text.substring(0, currentIndex));
    let firstDelay = true;

    useEffect(() => {
        if (firstDelay) { setTimeout(() => {firstDelay = false}, initialDelay) }
        if (currentIndex <= text.length) {
            const timeout = setTimeout(() => {
                setCurrentText(() => text.substring(0, currentIndex));
                setCurrentIndex(prevIndex => prevIndex + 1);
            }, delay);
    
            return () => clearTimeout(timeout);
        }
    }, [currentIndex, delay, text]);

    return (<span>{currentText}</span>);
}

export default TypeEffect;