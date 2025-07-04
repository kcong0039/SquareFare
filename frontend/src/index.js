import "./globals.css"; // Import the global CSS file
import React from "react";
import ReactDOM from "react-dom/client"; // Correct import for React 18
import MealPackingDisplay from "./components/meal-packing-display";

const root = ReactDOM.createRoot(document.getElementById("root")); // Use createRoot
console.log("Root element:", root)
root.render(<MealPackingDisplay />);