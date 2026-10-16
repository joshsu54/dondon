using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

namespace XiuXian.Editor
{
    public static class PrototypeSceneBuilder
    {
        [MenuItem("XiuXian/Create Prototype Scene")]
        public static void CreateScene()
        {
            if (EditorApplication.isPlayingOrWillChangePlaymode) return;
            if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
            const string root = "Assets/XiuXian/Generated";
            if (!AssetDatabase.IsValidFolder(root)) AssetDatabase.CreateFolder("Assets/XiuXian", "Generated");
            string folder = AssetDatabase.GenerateUniqueAssetPath(root + "/Prototype");
            AssetDatabase.CreateFolder(root, System.IO.Path.GetFileName(folder));
            Shader shader = Shader.Find(GraphicsSettings.currentRenderPipeline == null
                ? "Standard" : "Universal Render Pipeline/Lit");
            if (shader == null)
            {
                EditorUtility.DisplayDialog("Unsupported render pipeline",
                    "Use a Universal 3D (URP) or Built-in 3D project for this prototype.", "OK");
                return;
            }
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            Material grass = MakeMaterial(folder, shader, "Grass", new Color(0.26f, 0.40f, 0.27f));
            Material stone = MakeMaterial(folder, shader, "Stone", new Color(0.50f, 0.53f, 0.53f));
            Material wood = MakeMaterial(folder, shader, "Wood", new Color(0.42f, 0.28f, 0.19f));
            Material roof = MakeMaterial(folder, shader, "Roof", new Color(0.18f, 0.27f, 0.30f));
            Material jade = MakeMaterial(folder, shader, "Jade", new Color(0.15f, 0.75f, 0.65f));

            Block("Ground", new Vector3(0, -0.5f, 15), new Vector3(90, 1, 100), grass);
            Block("Town Road", new Vector3(0, 0.015f, 0), new Vector3(7, 0.03f, 45), stone);
            string[] buildings = { "Blacksmith", "Market", "Kitchen", "Inn" };
            for (int i = 0; i < buildings.Length; i++)
            {
                float x = i % 2 == 0 ? -10 : 10;
                float z = -8 + (i / 2) * 15;
                Block(buildings[i] + " Placeholder", new Vector3(x, 2, z), new Vector3(8, 4, 9), wood);
                Block(buildings[i] + " Roof", new Vector3(x, 4.3f, z), new Vector3(9, 0.6f, 10), roof);
            }
            Block("Sect Gate Left", new Vector3(-4, 3, 35), new Vector3(1.5f, 6, 2), stone);
            Block("Sect Gate Right", new Vector3(4, 3, 35), new Vector3(1.5f, 6, 2), stone);
            Block("Sect Gate Lintel", new Vector3(0, 6, 35), new Vector3(11, 1, 3), roof);
            Block("Secret Realm Marker", new Vector3(25, 2, 40), new Vector3(3, 4, 1), jade);
            for (int i = 0; i < 5; i++)
                Block("Jump Step " + i, new Vector3(-22, 0.2f * (i + 1), 14 + i * 2),
                    new Vector3(4, 0.4f * (i + 1), 2), stone);
            for (int i = 0; i < 12; i++)
            {
                Vector3 p = new Vector3(17 + (i % 4) * 6, 0, -15 + (i / 4) * 12);
                Block("Tree Trunk", p + Vector3.up * 1.5f, new Vector3(0.7f, 3, 0.7f), wood);
                Block("Tree Crown", p + Vector3.up * 4, new Vector3(3, 3, 3), grass);
            }

            var player = new GameObject("Player");
            player.layer = 2;
            player.transform.position = new Vector3(0, 0.1f, -18);
            var controller = player.AddComponent<CharacterController>();
            controller.height = 1.8f;
            controller.radius = 0.3f;
            controller.center = new Vector3(0, 0.9f, 0);
            controller.stepOffset = 0.35f;
            var visual = GameObject.CreatePrimitive(PrimitiveType.Capsule);
            visual.name = "Visual - Replace With Blender Model";
            visual.layer = 2;
            Object.DestroyImmediate(visual.GetComponent<Collider>());
            visual.transform.SetParent(player.transform, false);
            visual.transform.localPosition = new Vector3(0, 0.9f, 0);
            visual.transform.localScale = new Vector3(0.6f, 0.9f, 0.6f);
            visual.GetComponent<Renderer>().sharedMaterial = jade;
            var facing = Block("Facing Marker", Vector3.zero, Vector3.one, roof);
            Object.DestroyImmediate(facing.GetComponent<Collider>());
            facing.layer = 2;
            facing.transform.SetParent(visual.transform, false);
            facing.transform.localPosition = new Vector3(0, 0.3f, 0.5f);
            facing.transform.localScale = new Vector3(0.35f, 0.2f, 0.3f);

            var cameraObject = new GameObject("Main Camera");
            cameraObject.tag = "MainCamera";
            var camera = cameraObject.AddComponent<Camera>();
            camera.nearClipPlane = 0.05f;
            camera.farClipPlane = 250;
            cameraObject.AddComponent<AudioListener>();
            cameraObject.AddComponent<OrbitCamera>().target = player.transform;
            var motor = player.AddComponent<ThirdPersonMotor>();
            motor.cameraTransform = cameraObject.transform;
            motor.visual = visual.transform;
            cameraObject.transform.SetPositionAndRotation(new Vector3(0, 3, -23), Quaternion.Euler(18, 0, 0));

            var sun = new GameObject("Sun").AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.intensity = 1.2f;
            sun.shadows = LightShadows.Soft;
            sun.transform.rotation = Quaternion.Euler(45, -30, 0);
            RenderSettings.ambientMode = AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.55f, 0.60f, 0.65f);
            RenderSettings.sun = sun;
            bool saved = EditorSceneManager.SaveScene(scene, folder + "/XiuXianPrototype.unity");
            AssetDatabase.SaveAssets();
            Selection.activeGameObject = player;
            if (SceneView.lastActiveSceneView != null) SceneView.lastActiveSceneView.FrameSelected();
            if (saved) Debug.Log("Prototype saved to " + folder + ". Press Play to explore.");
            else Debug.LogError("Scene save failed. Save the open scene manually before closing Unity.");
        }

        private static Material MakeMaterial(string folder, Shader shader, string name, Color color)
        {
            var material = new Material(shader) { color = color };
            AssetDatabase.CreateAsset(material, folder + "/" + name + ".mat");
            return material;
        }

        private static GameObject Block(string name, Vector3 position, Vector3 size, Material material)
        {
            var obj = GameObject.CreatePrimitive(PrimitiveType.Cube);
            obj.name = name;
            obj.transform.position = position;
            obj.transform.localScale = size;
            obj.GetComponent<Renderer>().sharedMaterial = material;
            return obj;
        }
    }
}
