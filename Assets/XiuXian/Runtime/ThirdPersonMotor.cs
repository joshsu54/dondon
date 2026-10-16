using UnityEngine;

namespace XiuXian
{
    [RequireComponent(typeof(CharacterController))]
    public sealed class ThirdPersonMotor : MonoBehaviour
    {
        public Transform cameraTransform;
        public Transform visual;
        [Min(0)] public float walkSpeed = 4f;
        [Min(0)] public float runSpeed = 7f;
        [Min(0)] public float jumpHeight = 1.3f;
        public float gravity = -24f;
        private CharacterController controller;
        private float verticalSpeed;
        private Vector3 spawnPoint;

        private void Awake()
        {
            controller = GetComponent<CharacterController>();
            spawnPoint = transform.position;
            if (cameraTransform == null && Camera.main != null)
                cameraTransform = Camera.main.transform;
        }

        private void Update()
        {
            bool active = Application.isFocused && Cursor.lockState == CursorLockMode.Locked;
            Vector2 input = active ? PrototypeInput.Move : Vector2.zero;
            float yaw = cameraTransform != null ? cameraTransform.eulerAngles.y : 0;
            Vector3 direction = Quaternion.Euler(0, yaw, 0) * new Vector3(input.x, 0, input.y);
            if (visual != null && direction.sqrMagnitude > 0.001f)
                visual.rotation = Quaternion.Slerp(visual.rotation, Quaternion.LookRotation(direction),
                    1f - Mathf.Exp(-14f * Time.deltaTime));

            float acceleration = Mathf.Min(gravity, -0.01f);
            if (controller.isGrounded && verticalSpeed < 0) verticalSpeed = -2f;
            if (active && controller.isGrounded && PrototypeInput.Jump)
                verticalSpeed = Mathf.Sqrt(jumpHeight * -2f * acceleration);
            verticalSpeed += acceleration * Time.deltaTime;
            float speed = active && PrototypeInput.Sprint ? runSpeed : walkSpeed;
            CollisionFlags flags = controller.Move(
                (direction * speed + Vector3.up * verticalSpeed) * Time.deltaTime);
            if ((flags & CollisionFlags.Above) != 0 && verticalSpeed > 0) verticalSpeed = 0;

            if (transform.position.y < -15)
            {
                controller.enabled = false;
                transform.position = spawnPoint;
                verticalSpeed = 0;
                controller.enabled = true;
            }
        }
    }
}
