// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';

// Mock Canvas
import 'jest-canvas-mock';

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
    constructor(callback, options) {}
    observe(element) {
        return null;
    }
    disconnect() {
        return null;
    }
    unobserve(element) {
        return null;
    }
};
