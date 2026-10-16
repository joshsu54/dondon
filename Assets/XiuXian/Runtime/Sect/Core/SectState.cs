using System;
using System.Collections.Generic;

namespace XiuXian.Sect
{
    public enum BuildingKind { HerbGarden, SwordYard, AlchemyHall, MeditationHall }
    public enum SpiritRoot { Wood, Fire, Earth, Metal, Water }
    public enum Personality { Diligent, Bold, Calm }
    public enum RoomKind { Battle, Gathering, Story, Rest, Boss }
    public enum CombatAction { Attack, Technique, Guard, Pill }

    [Serializable]
    public sealed class Stock
    {
        public int wood, stone, herbs, pills, spirit, crystals;
        public Stock() { }
        public Stock(int wood = 0, int stone = 0, int herbs = 0, int pills = 0, int spirit = 0, int crystals = 0)
        { this.wood = wood; this.stone = stone; this.herbs = herbs; this.pills = pills; this.spirit = spirit; this.crystals = crystals; }
        public bool Covers(Stock c) => wood >= c.wood && stone >= c.stone && herbs >= c.herbs && pills >= c.pills && spirit >= c.spirit && crystals >= c.crystals;
        public void Add(Stock c)
        {
            wood = Math.Min(1000000, wood + c.wood); stone = Math.Min(1000000, stone + c.stone);
            herbs = Math.Min(1000000, herbs + c.herbs); pills = Math.Min(1000000, pills + c.pills);
            spirit = Math.Min(1000000, spirit + c.spirit); crystals = Math.Min(1000000, crystals + c.crystals);
        }
        public bool Spend(Stock c)
        {
            if (!Covers(c)) return false;
            wood -= c.wood; stone -= c.stone; herbs -= c.herbs; pills -= c.pills; spirit -= c.spirit; crystals -= c.crystals;
            return true;
        }
        public Stock Half() => new Stock(wood / 2, stone / 2, herbs / 2, pills / 2, spirit / 2, crystals / 2);
    }

    [Serializable]
    public sealed class SectBuilding
    {
        public int id, x, z, rotation;
        public BuildingKind kind;
    }

    [Serializable]
    public sealed class Disciple
    {
        public int id, buildingId, realm, cultivation, herbSkill, swordSkill, alchemySkill, meditationSkill;
        public string name, story;
        public SpiritRoot root;
        public Personality personality;
        public float workSeconds, injurySeconds;
        public int storyChoices, expeditionsWon;
    }

    [Serializable]
    public sealed class RealmRoom
    {
        public RoomKind kind;
        public SpiritRoot element;
        public int variant;
    }

    [Serializable]
    public sealed class Expedition
    {
        public int seed, discipleId, roomIndex, health, maxHealth, energy, enemyHealth, enemyMaxHealth, enemyAttack, turn;
        public bool roomResolved;
        public List<RealmRoom> rooms = new List<RealmRoom>();
        public Stock loot = new Stock();
        public string message;
    }

    [Serializable]
    public sealed class LocalSeason
    {
        public long startsUtc, endsUtc;
        public int score;
        public bool claimed;
    }

    [Serializable]
    public sealed class SectState
    {
        public int version = 1, randomState = 1, nextBuildingId = 1;
        public long observedUtc;
        public Stock stock = new Stock();
        public List<SectBuilding> buildings = new List<SectBuilding>();
        public List<Disciple> disciples = new List<Disciple>();
        public Expedition expedition;
        public LocalSeason season;
        public string earnedTitle = "初立山門";
        public int totalExpeditions;
    }

    public static class SectRules
    {
        public const int GridWidth = 9, GridDepth = 7;
        public const long SeasonSeconds = 72 * 60 * 60;
        public static readonly string[] BuildingNames = { "靈藥圃", "演武場", "煉丹房", "修煉台" };
        public static readonly string[] RootNames = { "木", "火", "土", "金", "水" };
        public static readonly string[] PersonalityNames = { "勤勉", "果敢", "沉靜" };
        public static readonly string[] RealmNames = { "引氣", "煉氣", "築基", "金丹" };
        public static Stock Cost(BuildingKind kind)
        {
            switch (kind)
            {
                case BuildingKind.HerbGarden: return new Stock(20, 10, spirit: 5);
                case BuildingKind.SwordYard: return new Stock(25, 15);
                case BuildingKind.AlchemyHall: return new Stock(30, 20, spirit: 10);
                case BuildingKind.MeditationHall: return new Stock(25, 20, spirit: 5);
                default: throw new ArgumentOutOfRangeException(nameof(kind));
            }
        }
        public static Stock BreakthroughCost(Disciple d) => new Stock(pills: 2 + d.realm, spirit: 5 + d.realm * 5, crystals: d.realm >= 1 ? 1 : 0);
        public static int CultivationNeeded(Disciple d) => 30 + d.realm * 30;
        public static string StockText(Stock s) => $"木 {s.wood}　石 {s.stone}　藥 {s.herbs}　丹 {s.pills}　靈石 {s.spirit}　晶髓 {s.crystals}";
        public static bool Overcomes(SpiritRoot a, SpiritRoot b) =>
            (a == SpiritRoot.Wood && b == SpiritRoot.Earth) || (a == SpiritRoot.Earth && b == SpiritRoot.Water) ||
            (a == SpiritRoot.Water && b == SpiritRoot.Fire) || (a == SpiritRoot.Fire && b == SpiritRoot.Metal) ||
            (a == SpiritRoot.Metal && b == SpiritRoot.Wood);
    }
}
