import React from "react"
import "./card.css"

const Card = React.forwardRef(({ className, ...props }, ref) => (
  <div ref={ref} className={`card ${className || ""}`} {...props} />
))
Card.displayName = "Card"

export { Card }
