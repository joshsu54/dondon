using UnityEngine;

namespace XiuXian
{
    public sealed class OrbitCamera : MonoBehaviour
    {
        public Transform target;
        public Vector3 focusOffset = new Vector3(0, 1.5f, 0);
        public float distance = 5f;
        public float sensitivity = 0.12f;
        // Player geometry uses Ignore Raycast (layer 2).
        public LayerMask obstacleMask = ~(1 << 2);
        private float yaw;
        private float pitch = 18f;

        private void Start()
        {
            if (target != null) yaw = target.eulerAngles.y;
            SetCursor(true);
        }

        private void Update()
        {
            if (PrototypeInput.ReleaseCursor) SetCursor(false);
            else if (Application.isFocused && PrototypeInput.CaptureCursor) SetCursor(true);
        }

        private void LateUpdate()
        {
            if (target == null) return;
            if (Application.isFocused && Cursor.lockState == CursorLockMode.Locked)
            {
                Vector2 look = PrototypeInput.Look * sensitivity;
                yaw += look.x;
                pitch = Mathf.Clamp(pitch - look.y, -25f, 70f);
                distance = Mathf.Clamp(distance - PrototypeInput.Scroll * 0.5f, 2f, 9f);
            }
            Quaternion rotation = Quaternion.Euler(pitch, yaw, 0);
            Vector3 focus = target.position + focusOffset;
            Vector3 backward = rotation * Vector3.back;
            float actualDistance = distance;
            if (Physics.SphereCast(focus, 0.2f, backward, out RaycastHit hit, distance,
                obstacleMask, QueryTriggerInteraction.Ignore))
                actualDistance = Mathf.Max(0, hit.distance - 0.05f);
            transform.SetPositionAndRotation(focus + backward * actualDistance, rotation);
        }

        private void OnApplicationFocus(bool focused)
        {
            if (!focused) SetCursor(false);
        }

        private void OnDisable() => SetCursor(false);

        private static void SetCursor(bool capture)
        {
            Cursor.lockState = capture ? CursorLockMode.Locked : CursorLockMode.None;
            Cursor.visible = !capture;
        }

        private void OnGUI()
        {
            GUI.Box(new Rect(12, 12, 430, 78),
                "XiuXian | Third-person prototype\nWASD Move   Shift Run   Space Jump\nMouse Look   Wheel Zoom   Esc Cursor   Click Resume");
        }
    }
}
