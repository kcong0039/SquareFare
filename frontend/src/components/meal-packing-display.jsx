"use client"

import React, { useState, useEffect } from "react"
import { Card } from "./ui/card"
import { Button } from "./ui/button"
import { MapPin, AlertCircle } from "lucide-react"
import { fetchLatestMeal } from "../lib/api"
import "./meal-packing-display.css"  // Add useEffect here

export default function MealPackingDisplay() {
    const [currentMeal, setCurrentMeal] = useState(null)
    const [currentStationNumber, setCurrentStationNumber] = useState(null)
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState(null)
  
    // Function to fetch meal data from backend
    const fetchMeal = async () => {
        setIsLoading(true)
        setError(null)
    
        try {
          // Use the API function to fetch meal data from the backend
          const meal = await fetchLatestMeal()

          console.log("things get changed")
          
          console.log("Received meal data:", meal)
    
          setCurrentMeal(meal)
          setCurrentStationNumber(meal.stationNumber)
        } catch (err) {
          setError("Failed to fetch meal data. Please try again.")
          console.error("Error fetching meal data:", err)
        } finally {
          setIsLoading(false)
        }
    }

    useEffect(() => {
        const poll = async () => {
          const meal = await fetchLatestMeal()
      
          // Only update state if new data is different
          if (JSON.stringify(meal) !== JSON.stringify(currentMeal)) {
            setCurrentMeal(meal)
          }
        }
      
        poll()
        const interval = setInterval(poll, 2000)
        return () => clearInterval(interval)
      }, [currentMeal])
      
      

    return (
        <div className="meal-packing-container">
            <Card className="meal-display-card">
                {isLoading ? (
                // Loading Screen
                <div className="loading-screen">
                    <h1 className="loading-title">Loading...</h1>
                    <p className="loading-text">Retrieving meal information</p>
                </div>
                ) : error ? (
                // Error Screen
                <div className="error-screen">
                    <AlertCircle className="error-icon" />
                    <h1 className="error-title">Error</h1>
                    <p className="error-text">{error}</p>
                    <Button className="try-again-button" onClick={() => setError(null)}>
                    Try Again
                    </Button>
                </div>
                ) : !currentMeal ? (
                // Ready to Scan Screen
                <div className="ready-screen">
                    <div className="station-display">
                        <MapPin className="station-icon" />
                    <h2 className="station-text">{currentStationNumber}</h2>
                    </div>
                    <h1 className="ready-title">Ready to Scan</h1>
                    <p className="ready-text">Scan barcode to display meal information</p>
                </div>
                ) : (
                // Information Display Screen
                <div className="meal-info-container">
                    {/* Header Section */}
                    <div className="meal-header">
                    {/* Client and Dish Info */}
                    <div className="meal-details">
                        <div className="meal-details-list">
                            <div className="meal-detail-item">{currentMeal.clientName}</div>
                            <div className="meal-detail-item">{currentMeal.dishName}</div>
                            <div className="meal-detail-item">
                                {currentMeal.mealType} - {currentMeal.dishNumber} - Station: {currentMeal.stationNumber}
                            </div>
                        </div>
                    </div>
        
                    {/* Dietary Restrictions */}
                    {currentMeal.dietaryRestrictions && (
                        <div className="dietary-restrictions">
                        <div className="dietary-title">DIETARY RESTRICTIONS:</div>
                        <div className="dietary-text">{currentMeal.dietaryRestrictions}</div>
                        </div>
                    )}
                    </div>
        
                    {/* Main Content */}
                    <div className="ingredients-container">
                        {/* Ingredients List */}
                        <div className="ingredients-list">
                            {currentMeal.ingredients.map((ingredient, index) => (
                                <div key={index} className="ingredient-card">
                                <h2 className="ingredient-name">{ingredient.name}</h2>
                                <p className="ingredient-portion">{ingredient.portion}</p>
                            </div>
                            ))}
                        </div>
                    </div>
                </div>
                )}
            </Card>
        </div>
    )
}  



