import React from "react";

export const Modal = ({ isOpen, title, message, type = "info", onConfirm, onCancel, confirmText = "Confirmar", cancelText = "Cancelar" }) => {
  if (!isOpen) return null;

  const bgColor = {
    info: "bg-blue-50",
    success: "bg-green-50",
    warning: "bg-yellow-50",
    error: "bg-red-50",
  }[type];

  const borderColor = {
    info: "border-blue-200",
    success: "border-green-200",
    warning: "border-yellow-200",
    error: "border-red-200",
  }[type];

  const iconColor = {
    info: "text-blue-600",
    success: "text-green-600",
    warning: "text-yellow-600",
    error: "text-red-600",
  }[type];

  const buttonColor = {
    info: "bg-blue-600 hover:bg-blue-700",
    success: "bg-green-600 hover:bg-green-700",
    warning: "bg-yellow-600 hover:bg-yellow-700",
    error: "bg-red-600 hover:bg-red-700",
  }[type];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className={`${bgColor} border ${borderColor} rounded-lg p-6 max-w-md w-full mx-4 shadow-lg`}>
        <div className="flex items-start gap-4">
          <div className={`${iconColor} text-2xl flex-shrink-0`}>
            {type === "success" && "✓"}
            {type === "error" && "✕"}
            {type === "warning" && "!"}
            {type === "info" && "ℹ"}
          </div>
          <div className="flex-1">
            {title && <h2 className="text-lg font-semibold text-gray-900 mb-2">{title}</h2>}
            {message && <p className="text-gray-700 mb-4">{message}</p>}
          </div>
        </div>
        <div className="flex gap-3 justify-end mt-6">
          {onCancel && (
            <button
              onClick={onCancel}
              className="px-4 py-2 rounded-md bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium transition"
            >
              {cancelText}
            </button>
          )}
          {onConfirm && (
            <button
              onClick={onConfirm}
              className={`px-4 py-2 rounded-md text-white font-medium transition ${buttonColor}`}
            >
              {confirmText}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default Modal;
