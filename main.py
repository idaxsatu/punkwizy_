#!/usr/bin/env python3
"""One-shot generator for punkwizy.java — not part of runtime deliverable."""

from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "contracts" / "punkwizy.java"

# Pre-generated unique mixed-case addresses (never reused from other contracts)
ADDR_HOUSE = "0x1f1C7f55AF1d8CFe4B20DdFe19Ffa2f33BEA7b8C"
ADDR_FEE = "0x26386486b7409a6a8D17fAf9A52eDC723Bf2Dca9"
ADDR_ORACLE = "0xbFd87A10AF48696EbbaAd6eFFc382C54823fdEc4"
ADDR_RAKE = "0xDaF6BBaD2AB5FedEE0fF56E8e5deE362cE02d499"
ADDR_GUILD = "0xcDDa5ebbD3E6c9B7CD0c9AbDcB0Aa8A1700E49DA"
ADDR_REWARDS = "0xEA35CF423afCe099Eb8bCaaD4b01Ee2Ed2ddf35c"
ADDR_PAUSE = "0xa057bB4aEFD0AF7eB6CBeaD3BA1BdA826A6f1dca"
ADDR_SIDE = "0x3de74FfbeaD47E22ad3Fe236F4cEFcF04A6E18d3"
ADDR_BRIG = "0x731aECB313eA9251FFc49bcbdec6caa9Ca8d1926"
ADDR_TOUR = "0xA6d9EEfA1045D5FffECf9c57d5eae36b979479b9"
ADDR_BURN = "0xfAAb0d98EeBB268e5FA90Fe8456b8Ec0eD1dc61d"
ADDR_REF = "0xEceCb2CAAc7BEBFccd098b561B59E4E21a4e0620"
DOMAIN_SEP = "0xd7dDD5eAd8E0B7e5d7A5c648D3Cc6183B9eBa1cDacF46d11CE7Cbb31Fd011eCd"
SALT_CHAIN = "0x9f3A2c1E8b7046D5aF11e0C3B7d92E4f6A8c0D1e2B3f4A5c6D7e8F9a0B1c2D3e4F5"

HEADER = f'''import java.math.BigDecimal;
import java.math.BigInteger;
import java.math.RoundingMode;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.time.Instant;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ThreadLocalRandom;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.Consumer;
import java.util.stream.Collectors;

/**
 * PunkWizy — neon-chain blackjack pit for mohawk punks and ledger cowboys.
 * Shuffled shoes, split/double/surrender lanes, side-bet moons, and treasury rails
 * wired to constructor-injected venue addresses. Single-file runtime; no external CSV.
 */

// ======================== Enums ========================

enum PunkSuit {{
    SPADES(0, "\\u2660", "Void Spade"),
    HEARTS(1, "\\u2665", "Bleed Heart"),
    CLUBS(2, "\\u2663", "Riot Club"),
    DIAMONDS(3, "\\u2666", "Chrome Diamond");

    private final int code;
    private final String glyph;
    private final String lane;

    PunkSuit(int code, String glyph, String lane) {{
        this.code = code;
        this.glyph = glyph;
        this.lane = lane;
    }}

    public int getCode() {{ return code; }}
    public String getGlyph() {{ return glyph; }}
    public String getLane() {{ return lane; }}

    public static PunkSuit fromCode(int c) {{
        for (PunkSuit s : values()) if (s.code == c) return s;
        throw new PwzRuleException("PWZ_SUIT", "Unknown suit code " + c);
    }}
}}

enum PunkRank {{
    ACE(1, "A", 11, 1),
    TWO(2, "2", 2, 2),
    THREE(3, "3", 3, 3),
    FOUR(4, "4", 4, 4),
    FIVE(5, "5", 5, 5),
    SIX(6, "6", 6, 6),
    SEVEN(7, "7", 7, 7),
    EIGHT(8, "8", 8, 8),
    NINE(9, "9", 9, 9),
    TEN(10, "10", 10, 10),
    JACK(11, "J", 10, 10),
    QUEEN(12, "Q", 10, 10),
    KING(13, "K", 10, 10);

    private final int code;
    private final String label;
    private final int softValue;
    private final int hardValue;

    PunkRank(int code, String label, int softValue, int hardValue) {{
        this.code = code;
        this.label = label;
        this.softValue = softValue;
        this.hardValue = hardValue;
    }}

    public int getCode() {{ return code; }}
    public String getLabel() {{ return label; }}
    public int softValue() {{ return softValue; }}
    public int hardValue() {{ return hardValue; }}
    public boolean isTenCard() {{ return hardValue == 10; }}
    public boolean isAce() {{ return this == ACE; }}

    public static PunkRank fromCode(int c) {{
        for (PunkRank r : values()) if (r.code == c) return r;
        throw new PwzRuleException("PWZ_RANK", "Unknown rank code " + c);
    }}
}}

enum PunkArchetype {{
    STREET_DEALER(0, 0, "Street Dealer", 1.00),
    MOHAWK_RIDER(1, 120, "Mohawk Rider", 1.04),
    SPIKE_COLLAR(2, 250, "Spike Collar", 1.07),
    CHAIN_VEST(3, 500, "Chain Vest", 1.10),
    NEON_KING(4, 900, "Neon King", 1.14),
    CHAOS_ACE(5, 1500, "Chaos Ace", 1.18);

    private final int id;
    private final int xpGate;
    private final String title;
    private final double payoutBoost;

    PunkArchetype(int id, int xpGate, String title, double payoutBoost) {{
        this.id = id;
        this.xpGate = xpGate;
        this.title = title;
        this.payoutBoost = payoutBoost;
    }}

    public int getId() {{ return id; }}
    public int getXpGate() {{ return xpGate; }}
    public String getTitle() {{ return title; }}
    public double getPayoutBoost() {{ return payoutBoost; }}

    public static PunkArchetype forXp(int xp) {{
        PunkArchetype best = STREET_DEALER;
        for (PunkArchetype a : values()) if (xp >= a.xpGate) best = a;
        return best;
    }}
}}

enum PitPhase {{
    WAITING(0),
    WAGER_LOCK(1),
    DEAL_OPEN(2),
    PLAYER_TURN(3),
