import { useState, useEffect } from 'react';
import './header.css'
import logo from '../../assets/logo.png'

export default function Header({ name }) {
    const getInitialTheme = () => {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark' || savedTheme === 'light') {
            return savedTheme;
        }
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    };

    const [theme, setTheme] = useState(getInitialTheme);
    useEffect(() => {
        const root = document.documentElement; 
        if (theme === 'light') {
            root.setAttribute('data-theme', 'dark');
        } else {
            root.removeAttribute('data-theme'); 
        }
        localStorage.setItem('theme', theme);
    }, [theme]);

    const toggleTheme = () => {
        setTheme(prev => prev === 'light' ? 'dark' : 'light');
    };

    return (
        <div className="header">

            <div className="header__content">
                <img 
  src={logo} 
  alt="Logo" 
/>
                <h1 className="header__title">{name}</h1>

                {/* <label htmlFor="theme-switch" className="switch">
                    <input
                        id="theme-switch"
                        type="checkbox"
                        checked={theme === 'dark'}
                        onChange={toggleTheme}
                        aria-label="Toggle dark mode"
                    />
                    <span className="slider"></span>
                    <span className="decoration"></span>
                </label> */}
            </div>
        </div>
    );
}
