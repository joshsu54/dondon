using UnityEngine;
#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

namespace XiuXian
{
    // Kept in one place so the prototype can later adopt rebindable Input Actions.
    public static class PrototypeInput
    {
        public static Vector2 Move
        {
            get
            {
#if ENABLE_INPUT_SYSTEM
                var k = Keyboard.current;
                if (k == null) return Vector2.zero;
                return Vector2.ClampMagnitude(new Vector2(
                    (k.dKey.isPressed ? 1 : 0) - (k.aKey.isPressed ? 1 : 0),
                    (k.wKey.isPressed ? 1 : 0) - (k.sKey.isPressed ? 1 : 0)), 1);
#else
                return Vector2.ClampMagnitude(new Vector2(
                    (Input.GetKey(KeyCode.D) ? 1 : 0) - (Input.GetKey(KeyCode.A) ? 1 : 0),
                    (Input.GetKey(KeyCode.W) ? 1 : 0) - (Input.GetKey(KeyCode.S) ? 1 : 0)), 1);
#endif
            }
        }

        public static Vector2 Look
        {
            get
            {
#if ENABLE_INPUT_SYSTEM
                return Mouse.current == null ? Vector2.zero : Mouse.current.delta.ReadValue();
#else
                return new Vector2(Input.GetAxisRaw("Mouse X"), Input.GetAxisRaw("Mouse Y")) * 20f;
#endif
            }
        }

        public static float Scroll
        {
            get
            {
#if ENABLE_INPUT_SYSTEM
                return Mouse.current == null ? 0 : Mathf.Sign(Mouse.current.scroll.ReadValue().y)
                    * (Mouse.current.scroll.ReadValue().y == 0 ? 0 : 1);
#else
                return Input.mouseScrollDelta.y;
#endif
            }
        }

        public static bool Sprint
        {
            get
            {
#if ENABLE_INPUT_SYSTEM
                return Keyboard.current != null && Keyboard.current.leftShiftKey.isPressed;
#else
                return Input.GetKey(KeyCode.LeftShift);
#endif
            }
        }

        public static bool Jump
        {
            get
            {
#if ENABLE_INPUT_SYSTEM
                return Keyboard.current != null && Keyboard.current.spaceKey.wasPressedThisFrame;
#else
                return Input.GetKeyDown(KeyCode.Space);
#endif
            }
        }

        public static bool ReleaseCursor
        {
            get
            {
#if ENABLE_INPUT_SYSTEM
                return Keyboard.current != null && Keyboard.current.escapeKey.wasPressedThisFrame;
#else
                return Input.GetKeyDown(KeyCode.Escape);
#endif
            }
        }

        public static bool CaptureCursor
        {
            get
            {
#if ENABLE_INPUT_SYSTEM
                return Mouse.current != null && Mouse.current.leftButton.wasPressedThisFrame;
#else
                return Input.GetMouseButtonDown(0);
#endif
            }
        }
    }
}
