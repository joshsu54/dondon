using System;
using System.Collections.Generic;

namespace XiuXian.Sect
{
    // Pure C#: independent of Unity scenes, frame timing, rendering and disk IO.
    public sealed class SectSimulation
    {
        public SectState State { get; }
        public SectSimulation(SectState state) { State = state ?? throw new ArgumentNullException(nameof(state)); }
        public static SectState NewGame(int seed, long utc)
        {
            var s = new SectState { randomState = seed == 0 ? 1 : seed, observedUtc = utc,
                stock = new Stock(140, 100, 12, 2, 40), season = new LocalSeason { startsUtc = utc, endsUtc = utc + SectRules.SeasonSeconds } };
            s.disciples.Add(new Disciple { id = 1, name = "林青禾", root = SpiritRoot.Wood, personality = Personality.Diligent,
                story = "山村採藥人出身，希望種出救治故鄉疫病的靈草。木靈根採藥額外產出。" });
            s.disciples.Add(new Disciple { id = 2, name = "沈長鋒", root = SpiritRoot.Metal, personality = Personality.Bold,
                story = "曾護送商隊穿越妖谷，立志以劍守護同門。金靈根提高戰鬥傷害。" });
            s.disciples.Add(new Disciple { id = 3, name = "蘇映丹", root = SpiritRoot.Fire, personality = Personality.Calm,
                story = "跟隨游方醫師長大，擅長控制爐火。火靈根每次煉丹多得一枚。" });
            s.disciples.Add(new Disciple { id = 4, name = "顧聽雨", root = SpiritRoot.Water, personality = Personality.Calm,
                story = "在古寺聽雨悟道，想找回失傳心法。水靈根修煉時多得修為。" });
            return s;
        }
        public Disciple Disciple(int id) => State.disciples.Find(d => d.id == id);
        public SectBuilding Building(int id) => State.buildings.Find(b => b.id == id);
        public bool IsExploring(int id) => State.expedition != null && State.expedition.discipleId == id;
        public long Observe(long utc) { State.observedUtc = Math.Max(State.observedUtc, utc); return State.observedUtc; }
        private void Score(int points) { if (State.observedUtc < State.season.endsUtc) State.season.score = Math.Min(1000000, State.season.score + points); }
        private int Random(int max)
        {
            uint x = unchecked((uint)State.randomState); x ^= x << 13; x ^= x >> 17; x ^= x << 5;
            State.randomState = unchecked((int)(x == 0 ? 1 : x));
            return (int)(unchecked((uint)State.randomState) % (uint)max);
        }
        public bool CanPlace(int x, int z, int ignoreId = 0) => x >= 0 && x < SectRules.GridWidth && z >= 0 && z < SectRules.GridDepth &&
            !State.buildings.Exists(b => b.id != ignoreId && b.x == x && b.z == z);
        public bool Build(BuildingKind kind, int x, int z, int rotation, out string message)
        {
            message = "此位置不能建造。";
            if (!Enum.IsDefined(typeof(BuildingKind), kind) || !CanPlace(x, z)) return false;
            if (!State.stock.Spend(SectRules.Cost(kind))) { message = "建材或靈石不足。"; return false; }
            State.buildings.Add(new SectBuilding { id = State.nextBuildingId++, x = x, z = z, rotation = ((rotation % 4) + 4) % 4, kind = kind });
            message = "已建造" + SectRules.BuildingNames[(int)kind] + "，可派弟子前往工作。"; return true;
        }
        public bool MoveBuilding(int id, int x, int z, int rotation, out string message)
        {
            var b = Building(id); message = "位置不可用。";
            if (b == null || !CanPlace(x, z, id)) return false;
            b.x = x; b.z = z; b.rotation = ((rotation % 4) + 4) % 4;
            foreach (var d in State.disciples) if (d.buildingId == id) d.workSeconds = 0;
            message = "建築已搬移，弟子將重新前往工作位置。"; return true;
        }
        public bool Assign(int discipleId, int buildingId, out string message)
        {
            var d = Disciple(discipleId); message = "無法派遣。";
            if (d == null || IsExploring(d.id) || (buildingId != 0 && Building(buildingId) == null)) return false;
            if (buildingId != 0 && State.disciples.Exists(other => other.id != d.id && other.buildingId == buildingId))
            { message = "這處設施已有弟子工作，每處容量一人。"; return false; }
            d.buildingId = buildingId; d.workSeconds = 0;
            message = buildingId == 0 ? "弟子回到待命區。" : "弟子正前往設施，到達後才會開始工作。"; return true;
        }
        public float WorkDuration(Disciple d)
        {
            var b = Building(d.buildingId); if (b == null) return 1;
            float seconds = b.kind == BuildingKind.AlchemyHall ? 12 : b.kind == BuildingKind.HerbGarden ? 8 : 10;
            if (d.personality == Personality.Diligent || (d.personality == Personality.Bold && b.kind == BuildingKind.SwordYard) ||
                (d.personality == Personality.Calm && b.kind == BuildingKind.MeditationHall)) seconds *= .85f;
            return seconds;
        }
        public void Advance(float seconds, long utc, ISet<int> arrived)
        {
            Observe(utc);
            if (float.IsNaN(seconds) || float.IsInfinity(seconds) || seconds <= 0) return;
            seconds = Math.Min(seconds, 1f); // No offline catch-up and no large frame-jump production.
            foreach (var d in State.disciples)
            {
                if (d.injurySeconds > 0) { d.injurySeconds = Math.Max(0, d.injurySeconds - seconds); continue; }
                if (IsExploring(d.id) || d.buildingId == 0 || arrived == null || !arrived.Contains(d.id)) continue;
                var b = Building(d.buildingId); if (b == null) continue;
                d.workSeconds += seconds;
                float duration = WorkDuration(d);
                if (d.workSeconds < duration) continue;
                if (b.kind == BuildingKind.AlchemyHall && State.stock.herbs < 3) { d.workSeconds = duration; continue; }
                d.workSeconds -= duration;
                switch (b.kind)
                {
                    case BuildingKind.HerbGarden:
                        State.stock.Add(new Stock(herbs: 2 + d.herbSkill / 10 + (d.root == SpiritRoot.Wood ? 1 : 0)));
                        d.herbSkill = Math.Min(50, d.herbSkill + 1); Score(2); break;
                    case BuildingKind.SwordYard:
                        d.swordSkill = Math.Min(50, d.swordSkill + 1); d.cultivation = Math.Min(10000, d.cultivation + 2); Score(2); break;
                    case BuildingKind.AlchemyHall:
                        State.stock.Spend(new Stock(herbs: 3)); State.stock.Add(new Stock(pills: d.root == SpiritRoot.Fire ? 2 : 1));
                        d.alchemySkill = Math.Min(50, d.alchemySkill + 1); Score(3); break;
                    case BuildingKind.MeditationHall:
                        d.cultivation = Math.Min(10000, d.cultivation + 4 + (d.root == SpiritRoot.Water ? 2 : 0));
                        d.meditationSkill = Math.Min(50, d.meditationSkill + 1); Score(2); break;
                }
            }
        }
        public bool Breakthrough(int id, out string message)
        {
            var d = Disciple(id); message = "暫時不能突破。";
            if (d == null || IsExploring(id) || d.realm >= 3 || d.injurySeconds > 0) return false;
            if (d.cultivation < SectRules.CultivationNeeded(d)) { message = "修為不足，先派往修煉台或演武場。"; return false; }
            if (!State.stock.Spend(SectRules.BreakthroughCost(d))) { message = "丹藥、靈石或晶髓不足。"; return false; }
            d.cultivation -= SectRules.CultivationNeeded(d); d.realm++; Score(25);
            message = d.name + "突破至" + SectRules.RealmNames[d.realm] + "，生命與戰鬥傷害提高。"; return true;
        }

        public bool StartExpedition(int id, out string message)
        {
            var d = Disciple(id); message = "弟子尚不能探索。";
            if (d == null || State.expedition != null || d.injurySeconds > 0) return false;
            if (!State.stock.Spend(new Stock(spirit: 3))) { message = "進入秘境需要 3 靈石。"; return false; }
            var run = new Expedition { discipleId = id, seed = Random(int.MaxValue), maxHealth = 65 + d.realm * 20, energy = 3 };
            run.health = run.maxHealth;
            for (int i = 0; i < 5; i++)
            {
                RoomKind kind = i == 4 ? RoomKind.Boss : i == 1 ? RoomKind.Battle : i == 2 ? (Random(2) == 0 ? RoomKind.Story : RoomKind.Rest) :
                    (Random(2) == 0 ? RoomKind.Gathering : RoomKind.Battle);
                run.rooms.Add(new RealmRoom { kind = kind, element = (SpiritRoot)Random(5), variant = Random(3) });
            }
            State.expedition = run; State.totalExpeditions++; EnterRoom();
            message = "進入秘境。此弟子暫停宗門工作，戰利品需帶回後才入庫。"; return true;
        }
        private void EnterRoom()
        {
            var r = State.expedition; var d = Disciple(r.discipleId); var room = r.rooms[r.roomIndex];
            r.turn = 0; r.roomResolved = false;
            bool boss = room.kind == RoomKind.Boss;
            r.enemyMaxHealth = boss ? 46 + d.realm * 14 : 23 + d.realm * 7 + room.variant * 3;
            r.enemyHealth = r.enemyMaxHealth; r.enemyAttack = boss ? 9 + d.realm * 2 : 5 + d.realm + room.variant;
            r.message = boss ? "守境首領現身。觀察敵方意圖，使用防禦應對蓄力。" : "探索新的秘境區域。";
        }
        public string EnemyIntent()
        {
            var r = State.expedition; if (r == null) return "";
            return r.turn % 3 == 1 ? "蓄力重擊（約雙倍傷害）" : r.turn % 3 == 2 ? "調息回血（本回合不攻擊）" : "普通攻擊";
        }
        public bool Act(CombatAction action, out string message)
        {
            var r = State.expedition; message = "現在不能戰鬥。";
            if (r == null || r.roomResolved || !Enum.IsDefined(typeof(CombatAction), action)) return false;
            var room = r.rooms[r.roomIndex];
            if (room.kind != RoomKind.Battle && room.kind != RoomKind.Boss) return false;
            var d = Disciple(r.discipleId);
            int damage = 9 + d.realm * 4 + d.swordSkill / 4 + (d.root == SpiritRoot.Metal ? 2 : 0) + (d.personality == Personality.Bold ? 1 : 0);
            bool guard = action == CombatAction.Guard;
            switch (action)
            {
                case CombatAction.Technique:
                    if (r.energy < 2) { message = "靈力不足。普攻或防禦可恢復一點。"; return false; }
                    r.energy -= 2; damage += 8 + (SectRules.Overcomes(d.root, room.element) ? 6 : 0); r.enemyHealth -= damage;
                    message = "施展五行劍訣，造成 " + damage + " 傷害。"; break;
                case CombatAction.Attack:
                    r.enemyHealth -= damage; r.energy = Math.Min(3, r.energy + 1); message = "普攻造成 " + damage + " 傷害。"; break;
                case CombatAction.Guard:
                    r.energy = Math.Min(3, r.energy + 1); message = "凝神防禦，減傷 75% 並恢復一點靈力。"; break;
                case CombatAction.Pill:
                    if (r.health == r.maxHealth) { message = "目前生命已滿。"; return false; }
                    if (!State.stock.Spend(new Stock(pills: 1))) { message = "宗門沒有可用丹藥。"; return false; }
                    r.health = Math.Min(r.maxHealth, r.health + 30); message = "服丹恢復 30 生命。"; break;
            }
            if (r.enemyHealth <= 0)
            {
                r.enemyHealth = 0; r.roomResolved = true;
                r.loot.Add(new Stock(wood: 12, stone: 9, herbs: 2, spirit: room.kind == RoomKind.Boss ? 12 : 4, crystals: room.kind == RoomKind.Boss ? 1 : 0));
                r.message = message + " 敵人倒下，戰利品已暫存。"; message = r.message; return true;
            }
            if (r.turn % 3 == 2)
            {
                r.enemyHealth = Math.Min(r.enemyMaxHealth, r.enemyHealth + 6); message += " 敵人調息恢復 6 生命。";
            }
            else
            {
                int incoming = r.enemyAttack * (r.turn % 3 == 1 ? 2 : 1);
                if (guard) incoming = Math.Max(1, incoming / 4);
                r.health = Math.Max(0, r.health - incoming); message += " 受到 " + incoming + " 傷害。";
            }
            r.turn++; r.message = message;
            if (r.health == 0)
            {
                d.injurySeconds = 30; State.expedition = null;
                message = "探索失敗，暫存戰利品遺失。弟子返回宗門，休養 30 秒後可再工作。";
            }
            return true;
        }
        public bool ChooseRoom(int choice, out string message)
        {
            var r = State.expedition; message = "此區域沒有這個選項。";
            if (r == null || r.roomResolved || choice < 0 || choice > 1) return false;
            var d = Disciple(r.discipleId); var room = r.rooms[r.roomIndex];
            switch (room.kind)
            {
                case RoomKind.Gathering:
                    if (choice == 0) { r.loot.Add(new Stock(wood: 18, stone: 14, herbs: 6 + d.herbSkill / 5)); message = "採集木石與靈草。採藥熟練度提高靈草收穫。"; }
                    else { r.loot.Add(new Stock(spirit: 8, crystals: 1)); r.health = Math.Max(1, r.health - 8); message = "冒險深入礦脈，獲得晶髓與靈石，損失 8 生命。"; }
                    break;
                case RoomKind.Story:
                    if (choice == 0)
                    {
                        if (!State.stock.Spend(new Stock(pills: 1))) { message = "救助受傷散修需要一枚丹藥。"; return false; }
                        r.loot.Add(new Stock(crystals: 1)); d.cultivation = Math.Min(10000, d.cultivation + 12); d.storyChoices++;
                        message = "你救助了受傷散修，獲贈晶髓。這段善緣留在弟子的成長紀錄中。";
                    }
                    else { r.loot.Add(new Stock(herbs: 4)); message = "保持距離，沿著線索找到四份靈草。"; }
                    break;
                case RoomKind.Rest:
                    if (choice == 0) { r.health = Math.Min(r.maxHealth, r.health + 25); message = "在靈泉休息，恢復 25 生命。"; }
                    else { r.energy = 3; d.cultivation = Math.Min(10000, d.cultivation + 8); message = "參悟古碑，靈力回滿並獲得 8 修為。"; }
                    break;
                default: return false;
            }
            r.roomResolved = true; r.message = message; return true;
        }
        public bool NextRoom(out string message)
        {
            var r = State.expedition; message = "先完成這個區域。";
            if (r == null || !r.roomResolved) return false;
            if (r.roomIndex == r.rooms.Count - 1)
            {
                var d = Disciple(r.discipleId); State.stock.Add(r.loot); d.expeditionsWon++;
                d.cultivation = Math.Min(10000, d.cultivation + 15); Score(60);
                message = "秘境通關！戰利品已入庫，弟子獲得 15 修為與一筆歷練紀錄。";
                State.expedition = null; return true;
            }
            r.roomIndex++; EnterRoom(); message = State.expedition.message; return true;
        }
        public bool Retreat(out string message)
        {
            var r = State.expedition; message = "目前沒有探索。";
            if (r == null) return false;
            State.stock.Add(r.loot.Half()); Disciple(r.discipleId).injurySeconds = 10; State.expedition = null;
            message = "撤回宗門，帶回暫存戰利品的一半；弟子休養 10 秒。"; return true;
        }
        public bool ClaimSeason(long utc, out string message)
        {
            Observe(utc); var s = State.season; message = "本期尚未結束，或獎勵已領取。";
            if (State.observedUtc < s.endsUtc || s.claimed) return false;
            s.claimed = true;
            int tier = s.score >= 1000 ? 3 : s.score >= 300 ? 2 : s.score >= 100 ? 1 : 0;
            string[] titles = { "初立山門", "勤修宗門", "青雲小宗", "萬象新秀" };
            State.earnedTitle = titles[tier]; State.stock.Add(new Stock(spirit: tier * 10, crystals: tier >= 2 ? 1 : 0));
            message = "本機賽季結算：" + State.earnedTitle + "。本期獎勵只能領一次。"; return true;
        }
        public bool NewSeason(long utc, out string message)
        {
            Observe(utc); message = "先結算上一期獎勵。";
            if (!State.season.claimed || State.observedUtc < State.season.endsUtc) return false;
            State.season = new LocalSeason { startsUtc = State.observedUtc, endsUtc = State.observedUtc + SectRules.SeasonSeconds };
            message = "新的 72 小時本機挑戰已開始。"; return true;
        }
    }
}
