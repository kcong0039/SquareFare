import React from "react"
import "./button.css"

export const Button = React.forwardRef(
  ({ className, variant = "default", size = "default", disabled, children, ...props }, ref) => {
    return (
      <button
        className={`button button-${variant} button-${size} ${disabled ? "button-disabled" : ""} ${className || ""}`}
        disabled={disabled}
        ref={ref}
        {...props}
      >
        {children}
      </button>
    )
  },
)
Button.displayName = "Button"
