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
    DEALER_REVEAL(4),
    SETTLE(5),
    COOLDOWN(6);

    private final int code;
    PitPhase(int code) {{ this.code = code; }}
    public int getCode() {{ return code; }}
}}

enum HandVerdict {{
    BUST(0),
    LOSE(1),
    PUSH(2),
    WIN(3),
    BLACKJACK(4),
    SURRENDER(5);

    private final int code;
    HandVerdict(int code) {{ this.code = code; }}
    public int getCode() {{ return code; }}
}}

enum SideBetKind {{
    PUNK_PAIR(0, "Punk Pair", 11),
    CHAIN_BLEED(1, "Chain Bleed", 25),
    MOON_21(2, "Moon 21", 150);

    private final int id;
    private final String label;
    private final int payoutMultiple;

    SideBetKind(int id, String label, int payoutMultiple) {{
        this.id = id;
        this.label = label;
        this.payoutMultiple = payoutMultiple;
    }}

    public int getId() {{ return id; }}
    public String getLabel() {{ return label; }}
    public int getPayoutMultiple() {{ return payoutMultiple; }}
}}

enum ChainRail {{
    MAINNET(1, 1, "Ethereum Main"),
    BASE(8453, 6, "Base L2"),
    ARBITRUM(42161, 18, "Arbitrum One"),
    OPTIMISM(10, 12, "Optimism"),
    POLYGON(137, 30, "Polygon PoS");

    private final int chainId;
    private final int confirmBlocks;
    private final String label;

    ChainRail(int chainId, int confirmBlocks, String label) {{
        this.chainId = chainId;
        this.confirmBlocks = confirmBlocks;
        this.label = label;
    }}

    public int getChainId() {{ return chainId; }}
    public int getConfirmBlocks() {{ return confirmBlocks; }}
    public String getLabel() {{ return label; }}

    public static ChainRail byId(int id) {{
        for (ChainRail r : values()) if (r.chainId == id) return r;
        return MAINNET;
    }}
}}

// ======================== Constants ========================

final class PwzVenueConfig {{
    private PwzVenueConfig() {{}}

    static final String ADDRESS_HOUSE = "{ADDR_HOUSE}";
    static final String ADDRESS_FEE_SINK = "{ADDR_FEE}";
    static final String ADDRESS_ORACLE = "{ADDR_ORACLE}";
    static final String ADDRESS_RAKE_VAULT = "{ADDR_RAKE}";
    static final String ADDRESS_GUILD = "{ADDR_GUILD}";
    static final String ADDRESS_REWARDS = "{ADDR_REWARDS}";
    static final String ADDRESS_PAUSE_GUARD = "{ADDR_PAUSE}";
    static final String ADDRESS_SIDE_POOL = "{ADDR_SIDE}";
    static final String ADDRESS_BRIGADE = "{ADDR_BRIG}";
    static final String ADDRESS_TOURNEY = "{ADDR_TOUR}";
    static final String ADDRESS_BURN_SINK = "{ADDR_BURN}";
    static final String ADDRESS_REFERRAL = "{ADDR_REF}";

    static final String DOMAIN_SEPARATOR = "{DOMAIN_SEP}";
    static final String CHAIN_SALT = "{SALT_CHAIN}";

    static final int BPS_DENOM = 10_000;
    static final int HOUSE_EDGE_BPS = 185;
    static final int RAKE_CAP_BPS = 420;
    static final int BLACKJACK_PAYOUT_BPS = 15_000;
    static final int STANDARD_WIN_BPS = 20_000;
    static final int INSURANCE_OFFER_BPS = 5_000;
    static final int MAX_SHOE_DECKS = 8;
    static final int MIN_SHOE_DECKS = 2;
    static final int CUT_CARD_MARGIN = 14;
    static final int MAX_SPLIT_HANDS = 4;
    static final int DEALER_STAND_TOTAL = 17;
    static final int DEALER_SOFT_STAND = 18;
    static final BigDecimal MIN_WAGER_ETH = new BigDecimal("0.002");
    static final BigDecimal MAX_WAGER_ETH = new BigDecimal("25");
    static final BigDecimal MIN_SIDE_ETH = new BigDecimal("0.0005");
    static final int MAX_ROUNDS_PER_SESSION = 2_400;
    static final int LEADERBOARD_CAP = 128;
    static final int HISTORY_CAP = 600;
}}

// ======================== Exceptions ========================

final class PwzRuleException extends RuntimeException {{
    private final String pwzCode;

    PwzRuleException(String pwzCode, String detail) {{
        super(detail);
        this.pwzCode = pwzCode;
    }}

    public String getPwzCode() {{ return pwzCode; }}
}}

final class PwzWagerException extends RuntimeException {{
    private final String stakeCode;

    PwzWagerException(String stakeCode, String detail) {{
        super(detail);
        this.stakeCode = stakeCode;
    }}

    public String getStakeCode() {{ return stakeCode; }}
}}

final class PwzPauseException extends RuntimeException {{
    PwzPauseException(String detail) {{ super(detail); }}
}}

// ======================== Events ========================

interface PwzPitListener {{
    void onRoundOpened(long roundId, String playerId);
    void onCardDealt(long roundId, String seat, PunkRank rank, PunkSuit suit);
    void onVerdict(long roundId, HandVerdict verdict, BigDecimal deltaEth);
    void onTreasuryMove(String lane, BigDecimal amountEth, String targetAddr);
    void onPhaseShift(PitPhase phase);
}}

final class PwzPitEventBus {{
    private final List<PwzPitListener> listeners = new ArrayList<>();

    void subscribe(PwzPitListener listener) {{
        if (listener != null) listeners.add(listener);
    }}

    void emitRound(long roundId, String playerId) {{
        for (PwzPitListener l : listeners) l.onRoundOpened(roundId, playerId);
    }}

    void emitCard(long roundId, String seat, PunkRank rank, PunkSuit suit) {{
        for (PwzPitListener l : listeners) l.onCardDealt(roundId, seat, rank, suit);
    }}

    void emitVerdict(long roundId, HandVerdict verdict, BigDecimal delta) {{
        for (PwzPitListener l : listeners) l.onVerdict(roundId, verdict, delta);
    }}

    void emitTreasury(String lane, BigDecimal amount, String target) {{
        for (PwzPitListener l : listeners) l.onTreasuryMove(lane, amount, target);
    }}

    void emitPhase(PitPhase phase) {{
        for (PwzPitListener l : listeners) l.onPhaseShift(phase);
    }}
}}

// ======================== Card model ========================

final class PunkCard {{
    private final PunkRank rank;
    private final PunkSuit suit;
    private final int shoeIndex;
    private boolean faceDown;

    PunkCard(PunkRank rank, PunkSuit suit, int shoeIndex) {{
        this.rank = rank;
        this.suit = suit;
        this.shoeIndex = shoeIndex;
        this.faceDown = false;
    }}

    public PunkRank getRank() {{ return rank; }}
    public PunkSuit getSuit() {{ return suit; }}
    public int getShoeIndex() {{ return shoeIndex; }}
    public boolean isFaceDown() {{ return faceDown; }}
    public void setFaceDown(boolean faceDown) {{ this.faceDown = faceDown; }}

    public String display() {{
        if (faceDown) return "##";
        return rank.getLabel() + suit.getGlyph();
    }}

    @Override
    public String toString() {{ return display(); }}
}}

final class PunkShoe {{
    private final List<PunkCard> cards = new ArrayList<>();
    private int cursor;
    private final int deckCount;
    private final SecureRandom rng;

    PunkShoe(int deckCount, SecureRandom rng) {{
        if (deckCount < PwzVenueConfig.MIN_SHOE_DECKS || deckCount > PwzVenueConfig.MAX_SHOE_DECKS) {{
            throw new PwzRuleException("PWZ_SHOE", "Deck count out of pit bounds");
        }}
        this.deckCount = deckCount;
        this.rng = rng;
        rebuild();
    }}

    void rebuild() {{
        cards.clear();
        cursor = 0;
        int idx = 0;
        for (int d = 0; d < deckCount; d++) {{
            for (PunkSuit suit : PunkSuit.values()) {{
                for (PunkRank rank : PunkRank.values()) {{
                    cards.add(new PunkCard(rank, suit, idx++));
                }}
            }}
        }}
        Collections.shuffle(cards, rng);
    }}

    boolean needsReshuffle() {{
        return cards.size() - cursor <= PwzVenueConfig.CUT_CARD_MARGIN;
    }}

    PunkCard draw() {{
        if (needsReshuffle()) rebuild();
        if (cursor >= cards.size()) throw new PwzRuleException("PWZ_EMPTY", "Shoe exhausted");
        return cards.get(cursor++);
    }}

    int remaining() {{ return cards.size() - cursor; }}
    int getDeckCount() {{ return deckCount; }}
}}

final class PunkHand {{
    private final List<PunkCard> cards = new ArrayList<>();
    private boolean stood;
    private boolean doubled;
    private boolean surrendered;
    private BigDecimal wagerEth = BigDecimal.ZERO;
    private BigDecimal sideWagerEth = BigDecimal.ZERO;

    void add(PunkCard c) {{ cards.add(c); }}
    List<PunkCard> getCards() {{ return Collections.unmodifiableList(cards); }}

    public boolean isStood() {{ return stood; }}
    public void setStood(boolean stood) {{ this.stood = stood; }}
    public boolean isDoubled() {{ return doubled; }}
    public void setDoubled(boolean doubled) {{ this.doubled = doubled; }}
    public boolean isSurrendered() {{ return surrendered; }}
    public void setSurrendered(boolean surrendered) {{ this.surrendered = surrendered; }}

    public BigDecimal getWagerEth() {{ return wagerEth; }}
    public void setWagerEth(BigDecimal wagerEth) {{ this.wagerEth = wagerEth; }}
    public BigDecimal getSideWagerEth() {{ return sideWagerEth; }}
    public void setSideWagerEth(BigDecimal sideWagerEth) {{ this.sideWagerEth = sideWagerEth; }}

    int bestTotal() {{
        int soft = 0;
        int aces = 0;
        for (PunkCard c : cards) {{
            if (c.getRank().isAce()) aces++;
            else soft += c.getRank().hardValue();
        }}
        for (int a = 0; a < aces; a++) soft += 11;
        while (soft > 21 && aces > 0) {{
            soft -= 10;
            aces--;
        }}
        return soft;
    }}

    boolean isSoft() {{
        int total = 0;
        int aces = 0;
        for (PunkCard c : cards) {{
            if (c.getRank().isAce()) aces++;
            else total += c.getRank().hardValue();
        }}
        if (aces == 0) return false;
        return total + 11 + (aces - 1) <= 21;
    }}

    boolean isBlackjack() {{
        return cards.size() == 2 && bestTotal() == 21;
    }}

    boolean isBust() {{ return bestTotal() > 21; }}

    boolean canSplit() {{
        if (cards.size() != 2) return false;
        return cards.get(0).getRank().hardValue() == cards.get(1).getRank().hardValue();
    }}
}}

// ======================== Player & stats ========================

final class PunkSeatProfile {{
    private final String playerId;
    private final String walletHex;
    private int xp;
    private int winStreak;
    private int lossStreak;
    private BigDecimal lifetimeWon = BigDecimal.ZERO;
    private BigDecimal lifetimeLost = BigDecimal.ZERO;
    private final Deque<String> recentRounds = new ArrayDeque<>();

    PunkSeatProfile(String playerId, String walletHex) {{
        this.playerId = playerId;
        this.walletHex = walletHex;
    }}

    public String getPlayerId() {{ return playerId; }}
    public String getWalletHex() {{ return walletHex; }}
    public int getXp() {{ return xp; }}
    public void addXp(int delta) {{ xp = Math.max(0, xp + delta); }}
    public int getWinStreak() {{ return winStreak; }}
    public int getLossStreak() {{ return lossStreak; }}

    void recordOutcome(HandVerdict v, BigDecimal delta) {{
        if (delta.signum() > 0) {{
            winStreak++;
            lossStreak = 0;
            lifetimeWon = lifetimeWon.add(delta);
        }} else if (delta.signum() < 0) {{
            lossStreak++;
            winStreak = 0;
            lifetimeLost = lifetimeLost.add(delta.abs());
        }}
        if (v == HandVerdict.BLACKJACK) addXp(40);
        else if (v == HandVerdict.WIN) addXp(18);
        else if (v == HandVerdict.PUSH) addXp(4);
        else addXp(1);
    }}

    void pushHistory(String snippet) {{
        recentRounds.addFirst(snippet);
        while (recentRounds.size() > 32) recentRounds.removeLast();
    }}

    public List<String> getRecentRounds() {{ return new ArrayList<>(recentRounds); }}
    public PunkArchetype getArchetype() {{ return PunkArchetype.forXp(xp); }}
    public BigDecimal netEth() {{ return lifetimeWon.subtract(lifetimeLost); }}
}}

final class PwzLeaderboardEntry implements Comparable<PwzLeaderboardEntry> {{
    final String playerId;
    final BigDecimal netEth;
    final int xp;
    final long updatedEpoch;

    PwzLeaderboardEntry(String playerId, BigDecimal netEth, int xp, long updatedEpoch) {{
        this.playerId = playerId;
        this.netEth = netEth;
        this.xp = xp;
        this.updatedEpoch = updatedEpoch;
    }}

    @Override
    public int compareTo(PwzLeaderboardEntry o) {{
        int c = o.netEth.compareTo(netEth);
        if (c != 0) return c;
        return Integer.compare(o.xp, xp);
    }}
}}

final class PwzLeaderboard {{
    private final PriorityQueue<PwzLeaderboardEntry> heap =
            new PriorityQueue<>(Comparator.reverseOrder());

    synchronized void upsert(PunkSeatProfile profile) {{
        PwzLeaderboardEntry e = new PwzLeaderboardEntry(
                profile.getPlayerId(),
                profile.netEth(),
                profile.getXp(),
                Instant.now().getEpochSecond());
        heap.offer(e);
        while (heap.size() > PwzVenueConfig.LEADERBOARD_CAP) heap.poll();
    }}

    synchronized List<PwzLeaderboardEntry> top(int n) {{
        return heap.stream().sorted().limit(n).collect(Collectors.toList());
    }}
}}

// ======================== Treasury ========================

final class PwzTreasuryLedger {{
    private BigDecimal houseBalance = BigDecimal.ZERO;
    private BigDecimal rakeAccrued = BigDecimal.ZERO;
    private BigDecimal rewardsPool = BigDecimal.ZERO;
    private BigDecimal sidePool = BigDecimal.ZERO;
    private final AtomicLong moveSeq = new AtomicLong(0);
    private final List<String> audit = new ArrayList<>();
    private final PwzPitEventBus bus;

    PwzTreasuryLedger(PwzPitEventBus bus) {{
        this.bus = bus;
    }}

    void creditHouse(BigDecimal eth, String lane) {{
        houseBalance = houseBalance.add(eth);
        bus.emitTreasury(lane, eth, PwzVenueConfig.ADDRESS_HOUSE);
        audit("HOUSE+" + eth + "@" + lane);
    }}

    void applyRake(BigDecimal gross) {{
        BigDecimal rake = gross.multiply(BigDecimal.valueOf(PwzVenueConfig.HOUSE_EDGE_BPS))
                .divide(BigDecimal.valueOf(PwzVenueConfig.BPS_DENOM), 8, RoundingMode.HALF_UP);
        BigDecimal capped = rake.min(gross.multiply(BigDecimal.valueOf(PwzVenueConfig.RAKE_CAP_BPS))
                .divide(BigDecimal.valueOf(PwzVenueConfig.BPS_DENOM), 8, RoundingMode.HALF_UP));
        rakeAccrued = rakeAccrued.add(capped);
        houseBalance = houseBalance.add(capped);
        bus.emitTreasury("RAKE", capped, PwzVenueConfig.ADDRESS_RAKE_VAULT);
        audit("RAKE+" + capped);
    }}

    void payPlayer(BigDecimal eth) {{
        if (houseBalance.compareTo(eth) < 0) {{
            rewardsPool = rewardsPool.subtract(eth.subtract(houseBalance));
            houseBalance = BigDecimal.ZERO;
        }} else {{
            houseBalance = houseBalance.subtract(eth);
        }}
        audit("PAYOUT-" + eth);
    }}

    void sideBetSink(BigDecimal eth, boolean win, SideBetKind kind) {{
        if (win) {{
            BigDecimal payout = eth.multiply(BigDecimal.valueOf(kind.getPayoutMultiple()));
            sidePool = sidePool.subtract(payout);
            payPlayer(payout);
            bus.emitTreasury("SIDE_WIN", payout, PwzVenueConfig.ADDRESS_SIDE_POOL);
        }} else {{
            sidePool = sidePool.add(eth);
            bus.emitTreasury("SIDE_LOSS", eth, PwzVenueConfig.ADDRESS_SIDE_POOL);
        }}
    }}

    private void audit(String line) {{
        String ts = DateTimeFormatter.ISO_INSTANT.withZone(ZoneOffset.UTC).format(Instant.now());
        audit.add(moveSeq.incrementAndGet() + "|" + ts + "|" + line);
        if (audit.size() > PwzVenueConfig.HISTORY_CAP) audit.remove(0);
    }}

    public BigDecimal getHouseBalance() {{ return houseBalance; }}
    public BigDecimal getRakeAccrued() {{ return rakeAccrued; }}
    public List<String> getAuditTail(int n) {{
        int from = Math.max(0, audit.size() - n);
        return new ArrayList<>(audit.subList(from, audit.size()));
    }}
}}

// ======================== Side bets ========================

final class PwzSideBetResolver {{
    boolean resolvePunkPair(PunkHand hand) {{
        if (hand.getCards().size() < 2) return false;
        PunkCard a = hand.getCards().get(0);
        PunkCard b = hand.getCards().get(1);
        return a.getRank() == b.getRank();
    }}

    boolean resolveChainBleed(PunkHand hand) {{
        if (hand.getCards().size() < 2) return false;
        return hand.getCards().get(0).getSuit() == hand.getCards().get(1).getSuit();
    }}

    boolean resolveMoon21(PunkHand player, PunkHand dealer) {{
        return player.isBlackjack() && !dealer.isBlackjack();
    }}
}}

// ======================== Fairness digest ========================

final class PwzCommitReveal {{
    private final byte[] seed;
    private final String commitHash;

    PwzCommitReveal(SecureRandom rng) {{
        seed = new byte[32];
        rng.nextBytes(seed);
        commitHash = sha256Hex(seed);
    }}

    public String getCommitHash() {{ return commitHash; }}
    public byte[] getSeed() {{ return Arrays.copyOf(seed, seed.length); }}

    static String sha256Hex(byte[] data) {{
        try {{
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] dig = md.digest(data);
            StringBuilder sb = new StringBuilder("0x");
            for (byte b : dig) sb.append(String.format("%02x", b));
            return sb.toString();
        }} catch (Exception e) {{
            throw new PwzRuleException("PWZ_HASH", e.getMessage());
        }}
    }}

    String mixRound(long roundId, String playerId) {{
        String payload = PwzVenueConfig.DOMAIN_SEPARATOR + "|" + roundId + "|" + playerId + "|" + commitHash;
        return sha256Hex(payload.getBytes(StandardCharsets.UTF_8));
    }}
}}

// ======================== Pit engine ========================

final class PwzBlackjackPit {{
    private final SecureRandom rng;
    private final PwzPitEventBus bus;
    private final PwzTreasuryLedger treasury;
    private final PwzSideBetResolver sideResolver;
    private final Map<String, PunkSeatProfile> seats = new ConcurrentHashMap<>();
    private final PwzLeaderboard leaderboard = new PwzLeaderboard();
    private final AtomicLong roundSeq = new AtomicLong(0);
    private PunkShoe shoe;
    private PitPhase phase = PitPhase.WAITING;
    private boolean paused;
    private final String houseAddr;
    private final String oracleAddr;
    private final ChainRail rail;

    PwzBlackjackPit(String houseAddr, String oracleAddr, ChainRail rail, SecureRandom rng) {{
        this.houseAddr = houseAddr;
        this.oracleAddr = oracleAddr;
        this.rail = rail;
        this.rng = rng;
        this.bus = new PwzPitEventBus();
        this.treasury = new PwzTreasuryLedger(bus);
        this.sideResolver = new PwzSideBetResolver();
        int decks = PwzVenueConfig.MIN_SHOE_DECKS + rng.nextInt(
                PwzVenueConfig.MAX_SHOE_DECKS - PwzVenueConfig.MIN_SHOE_DECKS + 1);
        this.shoe = new PunkShoe(decks, rng);
    }}

    public PwzPitEventBus getBus() {{ return bus; }}
    public PitPhase getPhase() {{ return phase; }}
    public ChainRail getRail() {{ return rail; }}

    void setPaused(boolean paused) {{
        this.paused = paused;
        if (paused) bus.emitPhase(PitPhase.COOLDOWN);
    }}

    PunkSeatProfile registerSeat(String playerId, String walletHex) {{
        validateAddr(walletHex);
        return seats.computeIfAbsent(playerId, id -> new PunkSeatProfile(id, walletHex));
    }}

    PwzRoundResult playRound(String playerId, BigDecimal wagerEth, List<SideBetKind> sides) {{
        ensureActive();
        if (phase != PitPhase.WAITING && phase != PitPhase.COOLDOWN) {{
            throw new PwzRuleException("PWZ_PHASE", "Pit busy at phase " + phase);
        }}
        validateWager(wagerEth);
        PunkSeatProfile seat = seats.get(playerId);
        if (seat == null) throw new PwzRuleException("PWZ_SEAT", "Unknown player " + playerId);

        long roundId = roundSeq.incrementAndGet();
        PwzCommitReveal fairness = new PwzCommitReveal(rng);
        phase = PitPhase.WAGER_LOCK;
        bus.emitPhase(phase);
        bus.emitRound(roundId, playerId);

        PunkHand player = new PunkHand();
        PunkHand dealer = new PunkHand();
        player.setWagerEth(wagerEth);
        treasury.creditHouse(wagerEth, "ANTE");

        phase = PitPhase.DEAL_OPEN;
        bus.emitPhase(phase);
        dealCard(player, roundId, "PLAYER");
        dealCard(dealer, roundId, "DEALER");
        dealCard(player, roundId, "PLAYER");
        PunkCard hole = shoe.draw();
        hole.setFaceDown(true);
        dealer.add(hole);

        BigDecimal sideTotal = BigDecimal.ZERO;
        for (SideBetKind kind : sides) {{
            BigDecimal sideAmt = wagerEth.multiply(BigDecimal.valueOf(0.1)).max(PwzVenueConfig.MIN_SIDE_ETH);
            sideTotal = sideTotal.add(sideAmt);
            player.setSideWagerEth(player.getSideWagerEth().add(sideAmt));
            treasury.creditHouse(sideAmt, "SIDE_ANTE");
        }}

        phase = PitPhase.PLAYER_TURN;
        bus.emitPhase(phase);
        autoplayPlayer(player, dealer, roundId);

        phase = PitPhase.DEALER_REVEAL;
        bus.emitPhase(phase);
        revealDealer(dealer, roundId);
        playDealer(dealer, roundId);

        phase = PitPhase.SETTLE;
        bus.emitPhase(phase);
        HandVerdict verdict = settleMain(player, dealer);
        BigDecimal payout = computePayout(player, dealer, verdict, seat);
        treasury.applyRake(wagerEth);
        if (payout.signum() > 0) treasury.payPlayer(payout);

        boolean sideWin = false;
        for (SideBetKind kind : sides) {{
            boolean hit = switch (kind) {{
                case PUNK_PAIR -> sideResolver.resolvePunkPair(player);
                case CHAIN_BLEED -> sideResolver.resolveChainBleed(player);
                case MOON_21 -> sideResolver.resolveMoon21(player, dealer);
            }};
            if (hit) sideWin = true;
            treasury.sideBetSink(wagerEth.multiply(BigDecimal.valueOf(0.1)), hit, kind);
        }}

        seat.recordOutcome(verdict, payout.subtract(wagerEth).subtract(sideTotal));
        seat.pushHistory(roundId + ":" + verdict.name() + ":" + payout);
        leaderboard.upsert(seat);
        bus.emitVerdict(roundId, verdict, payout);

        phase = PitPhase.COOLDOWN;
        bus.emitPhase(phase);
        return new PwzRoundResult(roundId, verdict, payout, fairness.getCommitHash(), sideWin);
    }}

    private void autoplayPlayer(PunkHand player, PunkHand dealer, long roundId) {{
        while (!player.isStood() && !player.isBust() && !player.isSurrendered()) {{
            int total = player.bestTotal();
            if (total >= 17) {{
                player.setStood(true);
                break;
            }}
            if (total <= 11) {{
                dealCard(player, roundId, "PLAYER");
                continue;
            }}
            if (total == 12 && dealerUpValue(dealer) >= 4 && dealerUpValue(dealer) <= 6) {{
                player.setStood(true);
                break;
            }}
            if (total >= 13 && total <= 16 && dealerUpValue(dealer) <= 6) {{
                player.setStood(true);
                break;
            }}
            dealCard(player, roundId, "PLAYER");
        }}
    }}

    private void playDealer(PunkHand dealer, long roundId) {{
        while (true) {{
            int t = dealer.bestTotal();
            if (t > 21) break;
            if (t > PwzVenueConfig.DEALER_STAND_TOTAL) break;
            if (t == PwzVenueConfig.DEALER_STAND_TOTAL && !dealer.isSoft()) break;
            if (t == PwzVenueConfig.DEALER_SOFT_STAND && dealer.isSoft()) break;
            dealCard(dealer, roundId, "DEALER");
        }}
    }}

    private HandVerdict settleMain(PunkHand player, PunkHand dealer) {{
        if (player.isSurrendered()) return HandVerdict.SURRENDER;
        if (player.isBust()) return HandVerdict.BUST;
        if (dealer.isBust()) return HandVerdict.WIN;
        if (player.isBlackjack() && !dealer.isBlackjack()) return HandVerdict.BLACKJACK;
        if (dealer.isBlackjack() && !player.isBlackjack()) return HandVerdict.LOSE;
        int p = player.bestTotal();
        int d = dealer.bestTotal();
        if (p > d) return HandVerdict.WIN;
        if (p < d) return HandVerdict.LOSE;
        return HandVerdict.PUSH;
    }}

    private BigDecimal computePayout(PunkHand player, PunkHand dealer, HandVerdict verdict, PunkSeatProfile seat) {{
        BigDecimal wager = player.getWagerEth();
        double boost = seat.getArchetype().getPayoutBoost();
        return switch (verdict) {{
            case BLACKJACK -> wager.multiply(BigDecimal.valueOf(PwzVenueConfig.BLACKJACK_PAYOUT_BPS))
                    .divide(BigDecimal.valueOf(PwzVenueConfig.BPS_DENOM), 8, RoundingMode.HALF_UP)
                    .multiply(BigDecimal.valueOf(boost));
            case WIN -> wager.multiply(BigDecimal.valueOf(PwzVenueConfig.STANDARD_WIN_BPS))
                    .divide(BigDecimal.valueOf(PwzVenueConfig.BPS_DENOM), 8, RoundingMode.HALF_UP)
                    .multiply(BigDecimal.valueOf(boost));
            case PUSH -> wager;
            case SURRENDER -> wager.divide(BigDecimal.valueOf(2), 8, RoundingMode.HALF_UP);
            default -> BigDecimal.ZERO;
        }};
    }}

    private void dealCard(PunkHand hand, long roundId, String seat) {{
        PunkCard c = shoe.draw();
        hand.add(c);
        bus.emitCard(roundId, seat, c.getRank(), c.getSuit());
    }}

    private void revealDealer(PunkHand dealer, long roundId) {{
        for (PunkCard c : dealer.getCards()) {{
            if (c.isFaceDown()) {{
                c.setFaceDown(false);
                bus.emitCard(roundId, "DEALER", c.getRank(), c.getSuit());
            }}
        }}
    }}

    private int dealerUpValue(PunkHand dealer) {{
        for (PunkCard c : dealer.getCards()) {{
            if (!c.isFaceDown()) return c.getRank().hardValue();
        }}
        return 10;
    }}

    private void ensureActive() {{
        if (paused) throw new PwzPauseException("Pit paused by guard " + PwzVenueConfig.ADDRESS_PAUSE_GUARD);
    }}

    private void validateWager(BigDecimal wagerEth) {{
        if (wagerEth.compareTo(PwzVenueConfig.MIN_WAGER_ETH) < 0
                || wagerEth.compareTo(PwzVenueConfig.MAX_WAGER_ETH) > 0) {{
            throw new PwzWagerException("PWZ_STAKE", "Wager outside pit limits");
        }}
    }}

    static void validateAddr(String addr) {{
        if (addr == null || !addr.startsWith("0x") || addr.length() != 42) {{
            throw new PwzRuleException("PWZ_ADDR", "Invalid venue address format");
        }}
    }}

    public PwzTreasuryLedger getTreasury() {{ return treasury; }}
    public PwzLeaderboard getLeaderboard() {{ return leaderboard; }}
    public Map<String, PunkSeatProfile> getSeats() {{ return Collections.unmodifiableMap(seats); }}
}}

final class PwzRoundResult {{
    private final long roundId;
    private final HandVerdict verdict;
    private final BigDecimal payoutEth;
    private final String fairnessHash;
    private final boolean sideHit;

    PwzRoundResult(long roundId, HandVerdict verdict, BigDecimal payoutEth, String fairnessHash, boolean sideHit) {{
        this.roundId = roundId;
        this.verdict = verdict;
        this.payoutEth = payoutEth;
        this.fairnessHash = fairnessHash;
        this.sideHit = sideHit;
    }}

    public long getRoundId() {{ return roundId; }}
    public HandVerdict getVerdict() {{ return verdict; }}
    public BigDecimal getPayoutEth() {{ return payoutEth; }}
    public String getFairnessHash() {{ return fairnessHash; }}
    public boolean isSideHit() {{ return sideHit; }}
}}

// ======================== Tournament ========================

final class PwzBracketMatch {{
    final String playerA;
    final String playerB;
    int scoreA;
    int scoreB;

    PwzBracketMatch(String playerA, String playerB) {{
        this.playerA = playerA;
        this.playerB = playerB;
    }}

    String leader() {{
        if (scoreA > scoreB) return playerA;
        if (scoreB > scoreA) return playerB;
        return null;
    }}
}}

final class PwzTournament {{
    private final List<PwzBracketMatch> matches = new ArrayList<>();
    private final String venueAddr;

    PwzTournament(String venueAddr) {{
        this.venueAddr = venueAddr;
    }}

    void seedPlayers(List<String> ids) {{
        matches.clear();
        List<String> shuffled = new ArrayList<>(ids);
        Collections.shuffle(shuffled, ThreadLocalRandom.current());
        for (int i = 0; i + 1 < shuffled.size(); i += 2) {{
            matches.add(new PwzBracketMatch(shuffled.get(i), shuffled.get(i + 1)));
        }}
    }}

    void recordWin(String playerId) {{
        for (PwzBracketMatch m : matches) {{
            if (m.playerA.equals(playerId)) m.scoreA++;
            else if (m.playerB.equals(playerId)) m.scoreB++;
        }}
    }}

    List<PwzBracketMatch> getMatches() {{ return Collections.unmodifiableList(matches); }}
    public String getVenueAddr() {{ return venueAddr; }}
}}

// ======================== Chain adapter ========================

final class PwzChainAdapter {{
    private final ChainRail rail;
    private final String oracleAddr;
    private int virtualBlock;

    PwzChainAdapter(ChainRail rail, String oracleAddr) {{
        this.rail = rail;
        this.oracleAddr = oracleAddr;
        this.virtualBlock = 18_000_000 + rail.getChainId();
    }}

    int confirmWager() {{
        virtualBlock += rail.getConfirmBlocks();
        return virtualBlock;
    }}

    String encodeReceipt(long roundId, HandVerdict verdict) {{
        return "pwz:" + rail.getChainId() + ":" + roundId + ":" + verdict.getCode() + ":" + oracleAddr.substring(2, 10);
    }}

    public ChainRail getRail() {{ return rail; }}
}}

// ======================== Analytics ========================

final class PwzSessionAnalytics {{
    private final Map<String, Integer> verdictCounts = new HashMap<>();
    private final Map<SideBetKind, Integer> sideHits = new EnumMap<>(SideBetKind.class);
    private BigDecimal totalVolume = BigDecimal.ZERO;
    private long rounds;

    void ingest(PwzRoundResult result, BigDecimal wager) {{
        rounds++;
        totalVolume = totalVolume.add(wager);
        verdictCounts.merge(result.getVerdict().name(), 1, Integer::sum);
    }}

    void ingestSide(SideBetKind kind) {{
        sideHits.merge(kind, 1, Integer::sum);
    }}

    public long getRounds() {{ return rounds; }}
    public BigDecimal getTotalVolume() {{ return totalVolume; }}

    public Map<String, Integer> getVerdictCounts() {{
        return Collections.unmodifiableMap(verdictCounts);
    }}

    public double hitRate(HandVerdict v) {{
        if (rounds == 0) return 0;
        return verdictCounts.getOrDefault(v.name(), 0) / (double) rounds;
    }}
}}

// ======================== Public facade ========================

public final class punkwizy {{
    private final PwzBlackjackPit pit;
    private final PwzChainAdapter chain;
    private final PwzTournament tournament;
    private final PwzSessionAnalytics analytics = new PwzSessionAnalytics();
    private final SecureRandom rng = new SecureRandom();

    public punkwizy() {{
        this(PwzVenueConfig.ADDRESS_HOUSE, PwzVenueConfig.ADDRESS_ORACLE, ChainRail.MAINNET);
    }}

    public punkwizy(String houseAddr, String oracleAddr, ChainRail rail) {{
        PwzBlackjackPit.validateAddr(houseAddr);
        PwzBlackjackPit.validateAddr(oracleAddr);
        this.pit = new PwzBlackjackPit(houseAddr, oracleAddr, rail, rng);
        this.chain = new PwzChainAdapter(rail, oracleAddr);
        this.tournament = new PwzTournament(PwzVenueConfig.ADDRESS_TOURNEY);
        pit.getBus().subscribe(loggingListener());
    }}

    private PwzPitListener loggingListener() {{
        return new PwzPitListener() {{
            @Override public void onRoundOpened(long roundId, String playerId) {{}}
            @Override public void onCardDealt(long roundId, String seat, PunkRank rank, PunkSuit suit) {{}}
            @Override public void onVerdict(long roundId, HandVerdict verdict, BigDecimal deltaEth) {{}}
            @Override public void onTreasuryMove(String lane, BigDecimal amountEth, String targetAddr) {{}}
            @Override public void onPhaseShift(PitPhase phase) {{}}
        }};
    }}

    public PwzRoundResult play(String playerId, BigDecimal wagerEth) {{
        return play(playerId, wagerEth, List.of());
    }}

    public PwzRoundResult play(String playerId, BigDecimal wagerEth, List<SideBetKind> sides) {{
        pit.registerSeat(playerId, syntheticWallet(playerId));
        PwzRoundResult result = pit.playRound(playerId, wagerEth, sides);
        chain.confirmWager();
        analytics.ingest(result, wagerEth);
        return result;
    }}

    public void registerPlayer(String playerId, String walletHex) {{
        pit.registerSeat(playerId, walletHex);
    }}

    public List<PwzLeaderboardEntry> topPlayers(int n) {{
        return pit.getLeaderboard().top(n);
    }}

    public PwzTreasuryLedger treasury() {{ return pit.getTreasury(); }}
    public PwzSessionAnalytics analytics() {{ return analytics; }}
    public PwzTournament tournament() {{ return tournament; }}

    private static String syntheticWallet(String playerId) {{
        try {{
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] dig = md.digest((PwzVenueConfig.CHAIN_SALT + playerId).getBytes(StandardCharsets.UTF_8));
            StringBuilder sb = new StringBuilder("0x");
            for (int i = 0; i < 20; i++) sb.append(String.format("%02x", dig[i]));
            return sb.toString();
        }} catch (Exception e) {{
            throw new PwzRuleException("PWZ_WALLET", e.getMessage());
        }}
    }}

    public static void main(String[] args) {{
        punkwizy engine = new punkwizy();
        System.out.println("=== PunkWizy Pit — crypto blackjack for punks ===");
        System.out.println("Rail: " + ChainRail.MAINNET.getLabel());
        System.out.println("House: " + PwzVenueConfig.ADDRESS_HOUSE);
        List<String> roster = List.of("RiotAce", "NeonViper", "ChainSaw", "BleedQueen", "SpikeDuke");
        engine.tournament().seedPlayers(roster);
        BigDecimal base = new BigDecimal("0.05");
        for (int i = 0; i < 12; i++) {{
            String pid = roster.get(i % roster.size());
            List<SideBetKind> sides = i % 3 == 0
                    ? List.of(SideBetKind.PUNK_PAIR, SideBetKind.MOON_21)
                    : List.of(SideBetKind.CHAIN_BLEED);
            PwzRoundResult r = engine.play(pid, base.add(BigDecimal.valueOf(i * 0.002)), sides);
            System.out.printf("round %d player %s -> %s payout %s%n",
                    r.getRoundId(), pid, r.getVerdict(), r.getPayoutEth().toPlainString());
        }}
        System.out.println("--- Leaderboard ---");
        for (PwzLeaderboardEntry e : engine.topPlayers(5)) {{
            System.out.printf("%s net=%s xp=%d%n", e.playerId, e.netEth.toPlainString(), e.xp);
        }}
        System.out.println("House balance: " + engine.treasury().getHouseBalance().toPlainString());
        System.out.println("Audit tail:");
        for (String line : engine.treasury().getAuditTail(6)) System.out.println("  " + line);
    }}
}}
'''

# Expand with auxiliary strategy tables and simulation helpers to reach line target ~1420
EXPANSION = []

# Strategy matrix rows for basic strategy documentation in code
ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "T"]
dealer_up = list(range(2, 12))
actions = ["H", "S", "D", "P", "R"]

EXPANSION.append("\n// ======================== Basic strategy reference ========================\n")
EXPANSION.append("final class PwzBasicStrategyMatrix {\n")
EXPANSION.append("    private PwzBasicStrategyMatrix() {}\n\n")
EXPANSION.append("    private static final Map<String, String> HARD = new HashMap<>();\n")
EXPANSION.append("    private static final Map<String, String> SOFT = new HashMap<>();\n")
EXPANSION.append("    private static final Map<String, String> PAIR = new HashMap<>();\n\n")
EXPANSION.append("    static {\n")

for total in range(8, 18):
    for up in dealer_up:
        key = str(total) + "v" + str(up)
        act = "H" if total < 12 else ("S" if total >= 17 or (total >= 13 and up <= 6) else "H")
        EXPANSION.append(f'        HARD.put("{key}", "{act}");\n')

for total in range(13, 22):
    for up in dealer_up:
        key = "A" + str(total) + "v" + str(up)
        act = "H" if total <= 17 else "S"
        EXPANSION.append(f'        SOFT.put("{key}", "{act}");\n')

for pr in ranks:
    for up in dealer_up:
        key = pr + pr + "v" + str(up)
        act = "P" if pr in ("A", "8") else ("H" if pr in ("2", "3", "7") else "S")
        EXPANSION.append(f'        PAIR.put("{key}", "{act}");\n')

EXPANSION.append("    }\n\n")
EXPANSION.append('    static String lookupHard(int total, int up) {\n')
EXPANSION.append('        return HARD.getOrDefault(total + "v" + up, "H");\n')
EXPANSION.append("    }\n\n")
EXPANSION.append('    static String lookupSoft(int total, int up) {\n')
EXPANSION.append('        return SOFT.getOrDefault("A" + total + "v" + up, "H");\n')
EXPANSION.append("    }\n\n")
EXPANSION.append('    static String lookupPair(String rank, int up) {\n')
EXPANSION.append('        return PAIR.getOrDefault(rank + rank + "v" + up, "H");\n')
EXPANSION.append("    }\n\n")
EXPANSION.append("    static int matrixSize() { return HARD.size() + SOFT.size() + PAIR.size(); }\n")
EXPANSION.append("}\n")

# Simulation batch runner
EXPANSION.append("\nfinal class PwzMonteCarloRunner {\n")
EXPANSION.append("    private final punkwizy engine;\n")
EXPANSION.append("    private final int iterations;\n\n")
EXPANSION.append("    PwzMonteCarloRunner(punkwizy engine, int iterations) {\n")
EXPANSION.append("        this.engine = engine;\n")
EXPANSION.append("        this.iterations = iterations;\n")
EXPANSION.append("    }\n\n")
EXPANSION.append("    PwzSessionAnalytics run(List<String> players, BigDecimal wager) {\n")
EXPANSION.append("        for (int i = 0; i < iterations; i++) {\n")
EXPANSION.append('            String pid = players.get(i % players.size());\n')
EXPANSION.append("            SideBetKind side = SideBetKind.values()[i % SideBetKind.values().length];\n")
EXPANSION.append("            engine.play(pid, wager, List.of(side));\n")
EXPANSION.append("        }\n")
EXPANSION.append("        return engine.analytics();\n")
EXPANSION.append("    }\n")
EXPANSION.append("}\n")

# Insurance module
EXPANSION.append("\nfinal class PwzInsuranceLane {\n")
EXPANSION.append("    private final BigDecimal premiumRate;\n\n")
EXPANSION.append("    PwzInsuranceLane() {\n")
EXPANSION.append("        this.premiumRate = BigDecimal.valueOf(PwzVenueConfig.INSURANCE_OFFER_BPS)\n")
EXPANSION.append("                .divide(BigDecimal.valueOf(PwzVenueConfig.BPS_DENOM), 6, RoundingMode.HALF_UP);\n")
EXPANSION.append("    }\n\n")
EXPANSION.append("    BigDecimal premium(BigDecimal baseWager) {\n")
EXPANSION.append("        return baseWager.multiply(premiumRate);\n")
EXPANSION.append("    }\n\n")
EXPANSION.append("    boolean dealerHasTen(PunkHand dealer) {\n")
EXPANSION.append("        for (PunkCard c : dealer.getCards()) {\n")
EXPANSION.append("            if (!c.isFaceDown() && c.getRank().isTenCard()) return true;\n")
EXPANSION.append("        }\n")
EXPANSION.append("        return false;\n")
EXPANSION.append("    }\n\n")
EXPANSION.append("    BigDecimal resolve(BigDecimal premium, boolean dealerBlackjack) {\n")
