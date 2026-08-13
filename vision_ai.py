# ===== VISION AI ENGINE =====
# Complete Chart Analysis System
# vision_ai.py

import io
import hashlib
import numpy as np
from PIL import Image, ImageStat, ImageFilter
import colorsys
import math
from collections import Counter

class VisionAI:
    """
    Strong Vision AI for Trading Chart Analysis
    - Chart validation
    - Candle detection
    - Pattern recognition
    - Trend analysis
    - Market structure
    - Support/Resistance
    - Volume analysis
    """

    def __init__(self):
        # Chart colors (common in trading platforms)
        self.bullish_colors = [
            (0, 128, 0), (0, 255, 0), (34, 139, 34),
            (50, 205, 50), (0, 200, 0), (76, 175, 80),
            (0, 150, 0), (46, 125, 50), (56, 142, 60),
            (102, 187, 106), (129, 199, 132), (67, 160, 71),
            (0, 230, 118), (0, 191, 165), (38, 166, 91)
        ]

        self.bearish_colors = [
            (255, 0, 0), (220, 20, 60), (178, 34, 34),
            (255, 69, 0), (200, 0, 0), (244, 67, 54),
            (229, 57, 53), (211, 47, 47), (198, 40, 40),
            (239, 83, 80), (229, 115, 115), (255, 82, 82),
            (255, 23, 68), (213, 0, 0), (183, 28, 28)
        ]

        self.neutral_colors = [
            (128, 128, 128), (169, 169, 169), (192, 192, 192),
            (211, 211, 211), (119, 136, 153), (112, 128, 144)
        ]

        # Chart background colors
        self.chart_bg_colors = [
            (0, 0, 0), (17, 17, 17), (25, 25, 25),
            (30, 30, 30), (40, 40, 40), (18, 18, 42),
            (255, 255, 255), (240, 240, 240), (248, 248, 248),
            (13, 17, 23), (22, 26, 37), (19, 23, 34),
            (28, 35, 49), (32, 39, 55), (16, 21, 34)
        ]

        # Doji/Pattern thresholds
        self.doji_threshold = 0.1
        self.long_wick_threshold = 2.5
        self.engulfing_threshold = 1.5

        # Previous analysis cache
        self.analysis_cache = {}

    # ============================================
    # ===== CHART VALIDATION =====
    # ============================================

    def is_valid_chart(self, image_bytes):
        """
        Check if uploaded image is a valid trading chart
        Returns True/False
        """
        try:
            img = Image.open(io.BytesIO(image_bytes))
            img = img.convert('RGB')
            width, height = img.size

            # Size check - too small can't be chart
            if width < 200 or height < 150:
                return False

            # Convert to numpy array
            img_array = np.array(img)

            # ===== Multiple validation checks =====
            score = 0
            total_checks = 8

            # Check 1: Chart background detection
            if self._has_chart_background(img_array):
                score += 1

            # Check 2: Color distribution (charts have specific color patterns)
            if self._has_chart_colors(img_array):
                score += 1

            # Check 3: Vertical structures (candles are vertical)
            if self._has_vertical_structures(img_array):
                score += 1.5

            # Check 4: Grid lines detection
            if self._has_grid_lines(img_array):
                score += 1

            # Check 5: Color clusters (green/red areas)
            if self._has_trading_color_clusters(img_array):
                score += 1.5

            # Check 6: Aspect ratio (charts are usually wider)
            if width / height >= 1.0:
                score += 0.5

            # Check 7: Edge density (charts have many edges)
            if self._has_high_edge_density(img):
                score += 1

            # Check 8: Repeating patterns (candles repeat)
            if self._has_repeating_patterns(img_array):
                score += 1.5

            # Need at least 4 out of 8 checks
            return score >= 4.0

        except Exception as e:
            print(f"Chart validation error: {e}")
            return False

    def _has_chart_background(self, img_array):
        """Check if image has common chart background colors"""
        # Sample center area
        h, w = img_array.shape[:2]
        center = img_array[h//4:3*h//4, w//4:3*w//4]

        # Get dominant color
        pixels = center.reshape(-1, 3)
        avg_color = np.mean(pixels, axis=0)

        # Check if matches common chart backgrounds
        for bg in self.chart_bg_colors:
            distance = np.sqrt(np.sum((avg_color - np.array(bg)) ** 2))
            if distance < 80:
                return True

        # Check for dark backgrounds
        if avg_color[0] < 60 and avg_color[1] < 60 and avg_color[2] < 80:
            return True

        # Check for white backgrounds
        if avg_color[0] > 200 and avg_color[1] > 200 and avg_color[2] > 200:
            return True

        return False

    def _has_chart_colors(self, img_array):
        """Check for green/red color distribution typical in charts"""
        pixels = img_array.reshape(-1, 3)
        total = len(pixels)

        green_count = 0
        red_count = 0

        # Sample every 10th pixel for speed
        for i in range(0, total, 10):
            r, g, b = pixels[i]

            # Green detection
            if g > r + 20 and g > b + 20 and g > 60:
                green_count += 1

            # Red detection
            if r > g + 20 and r > b + 20 and r > 60:
                red_count += 1

        sampled = total // 10
        green_ratio = green_count / sampled if sampled > 0 else 0
        red_ratio = red_count / sampled if sampled > 0 else 0

        # Charts typically have both green and red
        if green_ratio > 0.01 and red_ratio > 0.01:
            return True

        # Or significant amount of one
        if green_ratio > 0.03 or red_ratio > 0.03:
            return True

        return False

    def _has_vertical_structures(self, img_array):
        """Detect vertical candle-like structures"""
        gray = np.mean(img_array, axis=2).astype(np.uint8)
        h, w = gray.shape

        vertical_count = 0
        check_cols = range(0, w, max(1, w // 50))

        for col in check_cols:
            column = gray[:, col]

            # Look for alternating dark-light patterns (candle bodies + wicks)
            diffs = np.abs(np.diff(column.astype(int)))
            transitions = np.sum(diffs > 30)

            if transitions >= 3:
                vertical_count += 1

        return vertical_count > len(list(check_cols)) * 0.3

    def _has_grid_lines(self, img_array):
        """Detect horizontal/vertical grid lines"""
        gray = np.mean(img_array, axis=2).astype(np.uint8)
        h, w = gray.shape

        horizontal_lines = 0
        for row in range(0, h, max(1, h // 30)):
            line = gray[row, :]
            std = np.std(line)
            if std < 15:  # Very uniform = likely a grid line
                horizontal_lines += 1

        return horizontal_lines >= 2

    def _has_trading_color_clusters(self, img_array):
        """Detect clusters of green and red (candle bodies)"""
        h, w = img_array.shape[:2]

        # Scan horizontal strips
        green_strips = 0
        red_strips = 0

        for y in range(0, h, max(1, h // 20)):
            strip = img_array[y, :, :]
            for x in range(0, w, max(1, w // 30)):
                r, g, b = strip[x]

                if g > r + 30 and g > b + 20 and g > 50:
                    green_strips += 1
                elif r > g + 30 and r > b + 20 and r > 50:
                    red_strips += 1

        total_strips = (h // max(1, h // 20)) * (w // max(1, w // 30))
        if total_strips == 0:
            return False

        color_ratio = (green_strips + red_strips) / total_strips
        return color_ratio > 0.05

    def _has_high_edge_density(self, img):
        """Charts have many edges due to candles and lines"""
        gray = img.convert('L')
        edges = gray.filter(ImageFilter.FIND_EDGES)
        edge_array = np.array(edges)

        edge_pixels = np.sum(edge_array > 50)
        total_pixels = edge_array.size

        edge_ratio = edge_pixels / total_pixels
        return edge_ratio > 0.05

    def _has_repeating_patterns(self, img_array):
        """Detect repeating vertical structures (candles)"""
        gray = np.mean(img_array, axis=2).astype(np.uint8)
        h, w = gray.shape

        # Take a horizontal middle strip
        mid_strip = gray[h // 2, :]

        # Look for repeating peaks
        threshold = np.mean(mid_strip)
        above = mid_strip > threshold

        # Count transitions
        transitions = np.sum(np.abs(np.diff(above.astype(int))))
        return transitions > 10

    # ============================================
    # ===== SAME CHART / NEW CANDLE DETECTION =====
    # ============================================

    def detect_new_candle(self, image_bytes, last_hash):
        """
        Compare current chart with previous to detect new candles
        """
        try:
            current_hash = hashlib.md5(image_bytes).hexdigest()

            # Exact same image
            if current_hash == last_hash:
                return False

            # If hash is different, likely has new data
            img = Image.open(io.BytesIO(image_bytes))
            img = img.convert('RGB')
            img_array = np.array(img)

            # Check right edge for new candle
            h, w = img_array.shape[:2]
            right_section = img_array[:, int(w * 0.85):, :]

            # Analyze right section for candle presence
            has_candle = self._detect_candle_in_section(right_section)

            return has_candle

        except Exception as e:
            print(f"New candle detection error: {e}")
            return True  # Assume new if error

    def _detect_candle_in_section(self, section):
        """Check if a section contains candle-like structures"""
        h, w = section.shape[:2]

        green_pixels = 0
        red_pixels = 0
        total = 0

        for y in range(0, h, 3):
            for x in range(0, w, 3):
                r, g, b = section[y, x]
                total += 1

                if g > r + 20 and g > b + 15:
                    green_pixels += 1
                elif r > g + 20 and r > b + 15:
                    red_pixels += 1

        if total == 0:
            return False

        color_ratio = (green_pixels + red_pixels) / total
        return color_ratio > 0.02

    # ============================================
    # ===== FULL CHART ANALYSIS =====
    # ============================================

    def analyze_chart(self, image_bytes):
        """
        Complete chart analysis
        Returns dict with all chart data
        """
        try:
            img = Image.open(io.BytesIO(image_bytes))
            img = img.convert('RGB')
            img_array = np.array(img)
            h, w = img_array.shape[:2]

            # ===== Extract all chart data =====

            # 1. Detect candles
            candles = self._extract_candles(img_array)

            # 2. Detect trend
            trend = self._detect_trend(candles, img_array)

            # 3. Detect market structure
            structure = self._detect_market_structure(candles, img_array)

            # 4. Detect support/resistance
            sr_levels = self._detect_support_resistance(candles, img_array)

            # 5. Detect patterns
            patterns = self._detect_patterns(candles)

            # 6. Analyze volume (if visible)
            volume = self._analyze_volume(img_array)

            # 7. Detect indicators (if visible)
            indicators = self._detect_indicators(img_array)

            # 8. Calculate volatility
            volatility = self._calculate_volatility(candles, img_array)

            # 9. Detect consolidation/breakout
            consolidation = self._detect_consolidation(candles, img_array)

            # 10. Last candle analysis
            last_candle = self._analyze_last_candle(candles, img_array)

            # 11. Color ratio analysis
            color_analysis = self._analyze_color_ratio(img_array)

            # 12. Momentum analysis
            momentum = self._analyze_momentum(candles, img_array)

            # 13. Price action
            price_action = self._analyze_price_action(candles, img_array)

            return {
                'candles': candles,
                'trend': trend,
                'structure': structure,
                'support_resistance': sr_levels,
                'patterns': patterns,
                'volume': volume,
                'indicators': indicators,
                'volatility': volatility,
                'consolidation': consolidation,
                'last_candle': last_candle,
                'color_analysis': color_analysis,
                'momentum': momentum,
                'price_action': price_action,
                'image_size': (w, h)
            }

        except Exception as e:
            print(f"Chart analysis error: {e}")
            return self._default_chart_data()

    # ============================================
    # ===== CANDLE EXTRACTION =====
    # ============================================

    def _extract_candles(self, img_array):
        """
        Extract candle data from chart image
        Detects individual candles with body and wick info
        """
        h, w = img_array.shape[:2]
        candles = []

        # Define chart area (exclude margins)
        chart_left = int(w * 0.08)
        chart_right = int(w * 0.92)
        chart_top = int(h * 0.05)
        chart_bottom = int(h * 0.85)

        chart_area = img_array[chart_top:chart_bottom, chart_left:chart_right]
        ch, cw = chart_area.shape[:2]

        # Scan columns to find candles
        col_step = max(1, cw // 100)
        candle_columns = []

        for x in range(0, cw, col_step):
            column = chart_area[:, x, :]

            green_count = 0
            red_count = 0
            total = len(column)

            for pixel in column:
                r, g, b = pixel

                if g > r + 25 and g > b + 15 and g > 50:
                    green_count += 1
                elif r > g + 25 and r > b + 15 and r > 50:
                    red_count += 1

            if green_count > total * 0.03 or red_count > total * 0.03:
                candle_type = 'bullish' if green_count > red_count else 'bearish'
                color_strength = max(green_count, red_count) / total

                # Find body boundaries
                body_top, body_bottom = self._find_candle_body(column, candle_type)
                wick_top, wick_bottom = self._find_candle_wicks(column, body_top, body_bottom, candle_type)

                body_size = abs(body_bottom - body_top) / ch if ch > 0 else 0
                upper_wick = abs(body_top - wick_top) / ch if ch > 0 else 0
                lower_wick = abs(wick_bottom - body_bottom) / ch if ch > 0 else 0

                candle_columns.append({
                    'x': x,
                    'type': candle_type,
                    'body_size': body_size,
                    'upper_wick': upper_wick,
                    'lower_wick': lower_wick,
                    'body_top': body_top / ch if ch > 0 else 0,
                    'body_bottom': body_bottom / ch if ch > 0 else 0,
                    'color_strength': color_strength,
                    'position': x / cw if cw > 0 else 0  # 0=left, 1=right
                })

        # Merge nearby columns into single candles
        candles = self._merge_candle_columns(candle_columns)

        return candles

    def _find_candle_body(self, column, candle_type):
        """Find the top and bottom of candle body"""
        h = len(column)
        body_pixels = []

        for y in range(h):
            r, g, b = column[y]

            if candle_type == 'bullish' and g > r + 20 and g > b + 10 and g > 50:
                body_pixels.append(y)
            elif candle_type == 'bearish' and r > g + 20 and r > b + 10 and r > 50:
                body_pixels.append(y)

        if body_pixels:
            return min(body_pixels), max(body_pixels)
        return h // 2, h // 2

    def _find_candle_wicks(self, column, body_top, body_bottom, candle_type):
        """Find wick extent above and below body"""
        h = len(column)

        # Upper wick - look above body
        wick_top = body_top
        for y in range(body_top - 1, -1, -1):
            r, g, b = column[y]
            brightness = (int(r) + int(g) + int(b)) / 3

            # Wick is usually thin and lighter
            if brightness > 40 and brightness < 200:
                # Check if it's a thin line (not background)
                if abs(int(r) - int(g)) < 50 and abs(int(g) - int(b)) < 50:
                    wick_top = y
                else:
                    break
            else:
                break

        # Lower wick - look below body
        wick_bottom = body_bottom
        for y in range(body_bottom + 1, h):
            r, g, b = column[y]
            brightness = (int(r) + int(g) + int(b)) / 3

            if brightness > 40 and brightness < 200:
                if abs(int(r) - int(g)) < 50 and abs(int(g) - int(b)) < 50:
                    wick_bottom = y
                else:
                    break
            else:
                break

        return wick_top, wick_bottom

    def _merge_candle_columns(self, columns):
        """Merge nearby column detections into candles"""
        if not columns:
            return []

        candles = []
        current_group = [columns[0]]

        for i in range(1, len(columns)):
            if columns[i]['x'] - columns[i-1]['x'] <= 5:
                current_group.append(columns[i])
            else:
                candles.append(self._merge_group(current_group))
                current_group = [columns[i]]

        if current_group:
            candles.append(self._merge_group(current_group))

        return candles

    def _merge_group(self, group):
        """Merge a group of columns into one candle"""
        types = [c['type'] for c in group]
        dominant_type = max(set(types), key=types.count)

        return {
            'type': dominant_type,
            'body_size': np.mean([c['body_size'] for c in group]),
            'upper_wick': np.mean([c['upper_wick'] for c in group]),
            'lower_wick': np.mean([c['lower_wick'] for c in group]),
            'body_top': np.mean([c['body_top'] for c in group]),
            'body_bottom': np.mean([c['body_bottom'] for c in group]),
            'color_strength': np.mean([c['color_strength'] for c in group]),
            'position': np.mean([c['position'] for c in group]),
            'width': len(group)
        }

    # ============================================
    # ===== TREND DETECTION =====
    # ============================================

    def _detect_trend(self, candles, img_array):
        """
        Detect overall market trend
        Returns: 'uptrend', 'downtrend', 'sideways'
        """
        if len(candles) < 3:
            return self._detect_trend_from_image(img_array)

        # Method 1: Candle body positions
        positions = [c['body_bottom'] for c in candles]

        # Higher positions = lower on screen = higher prices
        # (In image, y increases downward)
        first_half = positions[:len(positions)//2]
        second_half = positions[len(positions)//2:]

        avg_first = np.mean(first_half)
        avg_second = np.mean(second_half)

        # Method 2: Count bullish vs bearish
        bullish_count = sum(1 for c in candles if c['type'] == 'bullish')
        bearish_count = sum(1 for c in candles if c['type'] == 'bearish')
        total = len(candles)

        # Method 3: Recent candles weight more
        recent = candles[-5:] if len(candles) >= 5 else candles[-3:]
        recent_bullish = sum(1 for c in recent if c['type'] == 'bullish')
        recent_bearish = sum(1 for c in recent if c['type'] == 'bearish')

        # Combine methods
        trend_score = 0

        # Position analysis (inverted because y is inverted)
        if avg_second < avg_first - 0.02:
            trend_score += 2  # Uptrend
        elif avg_second > avg_first + 0.02:
            trend_score -= 2  # Downtrend

        # Candle count
        if bullish_count > bearish_count * 1.3:
            trend_score += 1
        elif bearish_count > bullish_count * 1.3:
            trend_score -= 1

        # Recent trend
        if recent_bullish > recent_bearish:
            trend_score += 1.5
        elif recent_bearish > recent_bullish:
            trend_score -= 1.5

        # Determine trend
        if trend_score >= 2:
            return {
                'direction': 'uptrend',
                'strength': min(abs(trend_score) / 5, 1.0),
                'bullish_count': bullish_count,
                'bearish_count': bearish_count
            }
        elif trend_score <= -2:
            return {
                'direction': 'downtrend',
                'strength': min(abs(trend_score) / 5, 1.0),
                'bullish_count': bullish_count,
                'bearish_count': bearish_count
            }
        else:
            return {
                'direction': 'sideways',
                'strength': 0.3,
                'bullish_count': bullish_count,
                'bearish_count': bearish_count
            }

    def _detect_trend_from_image(self, img_array):
        """Fallback trend detection using image color analysis"""
        h, w = img_array.shape[:2]

        # Analyze left half vs right half
        left_half = img_array[:, :w//2, :]
        right_half = img_array[:, w//2:, :]

        left_green = self._count_color_pixels(left_half, 'green')
        left_red = self._count_color_pixels(left_half, 'red')
        right_green = self._count_color_pixels(right_half, 'green')
        right_red = self._count_color_pixels(right_half, 'red')

        if right_green > right_red * 1.3:
            return {'direction': 'uptrend', 'strength': 0.6, 'bullish_count': 0, 'bearish_count': 0}
        elif right_red > right_green * 1.3:
            return {'direction': 'downtrend', 'strength': 0.6, 'bullish_count': 0, 'bearish_count': 0}
        else:
            return {'direction': 'sideways', 'strength': 0.3, 'bullish_count': 0, 'bearish_count': 0}

    def _count_color_pixels(self, section, color):
        """Count green or red pixels in a section"""
        count = 0
        h, w = section.shape[:2]

        for y in range(0, h, 5):
            for x in range(0, w, 5):
                r, g, b = section[y, x]

                if color == 'green' and g > r + 20 and g > b + 15 and g > 50:
                    count += 1
                elif color == 'red' and r > g + 20 and r > b + 15 and r > 50:
                    count += 1

        return count

    # ============================================
    # ===== MARKET STRUCTURE =====
    # ============================================

    def _detect_market_structure(self, candles, img_array):
        """
        Detect Higher Highs, Higher Lows, Lower Highs, Lower Lows
        """
        if len(candles) < 5:
            return {
                'type': 'unclear',
                'higher_highs': False,
                'higher_lows': False,
                'lower_highs': False,
                'lower_lows': False,
                'strength': 0.3
            }

        # Get swing points
        highs = [c['body_top'] for c in candles]
        lows = [c['body_bottom'] for c in candles]

        # Find swing highs and lows
        swing_highs = []
        swing_lows = []

        for i in range(1, len(highs) - 1):
            if highs[i] < highs[i-1] and highs[i] < highs[i+1]:
                swing_highs.append(highs[i])
            if lows[i] > lows[i-1] and lows[i] > lows[i+1]:
                swing_lows.append(lows[i])

        # Analyze structure (inverted y-axis)
        higher_highs = False
        higher_lows = False
        lower_highs = False
        lower_lows = False

        if len(swing_highs) >= 2:
            # In image, lower y = higher price
            if swing_highs[-1] < swing_highs[-2]:
                higher_highs = True
            elif swing_highs[-1] > swing_highs[-2]:
                lower_highs = True

        if len(swing_lows) >= 2:
            if swing_lows[-1] < swing_lows[-2]:
                higher_lows = True
            elif swing_lows[-1] > swing_lows[-2]:
                lower_lows = True

        # Determine structure type
        if higher_highs and higher_lows:
            structure_type = 'bullish'
            strength = 0.8
        elif lower_highs and lower_lows:
            structure_type = 'bearish'
            strength = 0.8
        elif higher_highs and lower_lows:
            structure_type = 'expanding'
            strength = 0.4
        elif lower_highs and higher_lows:
            structure_type = 'contracting'
            strength = 0.4
        else:
            structure_type = 'unclear'
            strength = 0.3

        return {
            'type': structure_type,
            'higher_highs': higher_highs,
            'higher_lows': higher_lows,
            'lower_highs': lower_highs,
            'lower_lows': lower_lows,
            'strength': strength
        }

    # ============================================
    # ===== SUPPORT & RESISTANCE =====
    # ============================================

    def _detect_support_resistance(self, candles, img_array):
        """Detect support and resistance levels"""
        if len(candles) < 3:
            return {
                'support_levels': [],
                'resistance_levels': [],
                'near_support': False,
                'near_resistance': False,
                'at_level': None
            }

        # Collect all price points
        all_highs = [c['body_top'] for c in candles]
        all_lows = [c['body_bottom'] for c in candles]

        # Find clusters of similar prices
        resistance_levels = self._find_price_clusters(all_highs)
        support_levels = self._find_price_clusters(all_lows)

        # Check if last candle is near S/R
        last_candle = candles[-1]
        near_support = False
        near_resistance = False
        at_level = None

        tolerance = 0.02

        for level in support_levels:
            if abs(last_candle['body_bottom'] - level) < tolerance:
                near_support = True
                at_level = 'support'

        for level in resistance_levels:
            if abs(last_candle['body_top'] - level) < tolerance:
                near_resistance = True
                at_level = 'resistance'

        return {
            'support_levels': support_levels[:3],
            'resistance_levels': resistance_levels[:3],
            'near_support': near_support,
            'near_resistance': near_resistance,
            'at_level': at_level
        }

    def _find_price_clusters(self, prices):
        """Find price levels where multiple touches occurred"""
        if len(prices) < 2:
            return []

        clusters = []
        sorted_prices = sorted(prices)
        tolerance = 0.015

        i = 0
        while i < len(sorted_prices):
            cluster = [sorted_prices[i]]
            j = i + 1

            while j < len(sorted_prices) and sorted_prices[j] - sorted_prices[i] < tolerance:
                cluster.append(sorted_prices[j])
                j += 1

            if len(cluster) >= 2:
                clusters.append(np.mean(cluster))

            i = j

        return clusters

    # ============================================
    # ===== PATTERN DETECTION =====
    # ============================================

    def _detect_patterns(self, candles):
        """
        Detect candlestick patterns
        """
        patterns = []

        if len(candles) < 2:
            return patterns

        last = candles[-1]
        prev = candles[-2] if len(candles) >= 2 else None
        prev2 = candles[-3] if len(candles) >= 3 else None

        # ===== Single Candle Patterns =====

        # Doji
        if last['body_size'] < self.doji_threshold * 0.01:
            patterns.append({
                'name': 'Doji',
                'type': 'neutral',
                'reliability': 0.5
            })

        # Hammer (bullish)
        if (last['lower_wick'] > last['body_size'] * self.long_wick_threshold and
            last['upper_wick'] < last['body_size'] * 0.5):
            patterns.append({
                'name': 'Hammer',
                'type': 'bullish',
                'reliability': 0.7
            })

        # Inverted Hammer
        if (last['upper_wick'] > last['body_size'] * self.long_wick_threshold and
            last['lower_wick'] < last['body_size'] * 0.5):
            patterns.append({
                'name': 'Inverted Hammer',
                'type': 'bearish' if last['type'] == 'bearish' else 'bullish',
                'reliability': 0.6
            })

        # Shooting Star
        if (last['upper_wick'] > last['body_size'] * self.long_wick_threshold and
            last['lower_wick'] < last['body_size'] * 0.3 and
            last['type'] == 'bearish'):
            patterns.append({
                'name': 'Shooting Star',
                'type': 'bearish',
                'reliability': 0.7
            })

        # Marubozu (strong body, no wicks)
        if (last['upper_wick'] < last['body_size'] * 0.1 and
            last['lower_wick'] < last['body_size'] * 0.1 and
            last['body_size'] > 0.01):
            patterns.append({
                'name': 'Marubozu',
                'type': last['type'],
                'reliability': 0.8
            })

        # Long wick rejection
        total_wick = last['upper_wick'] + last['lower_wick']
        if total_wick > last['body_size'] * 3:
            patterns.append({
                'name': 'Long Wick Rejection',
                'type': 'bullish' if last['lower_wick'] > last['upper_wick'] else 'bearish',
                'reliability': 0.65
            })

        # ===== Two Candle Patterns =====

        if prev:
            # Engulfing
            if (last['body_size'] > prev['body_size'] * self.engulfing_threshold and
                last['type'] != prev['type']):
                patterns.append({
                    'name': f"{'Bullish' if last['type'] == 'bullish' else 'Bearish'} Engulfing",
                    'type': last['type'],
                    'reliability': 0.75
                })

            # Tweezer Top/Bottom
            if abs(last['body_top'] - prev['body_top']) < 0.005:
                patterns.append({
                    'name': 'Tweezer Top',
                    'type': 'bearish',
                    'reliability': 0.6
                })
            if abs(last['body_bottom'] - prev['body_bottom']) < 0.005:
                patterns.append({
                    'name': 'Tweezer Bottom',
                    'type': 'bullish',
                    'reliability': 0.6
                })

        # ===== Three Candle Patterns =====

        if prev and prev2:
            # Morning Star (bullish reversal)
            if (prev2['type'] == 'bearish' and
                prev['body_size'] < prev2['body_size'] * 0.3 and
                last['type'] == 'bullish' and
                last['body_size'] > prev['body_size']):
                patterns.append({
                    'name': 'Morning Star',
                    'type': 'bullish',
                    'reliability': 0.8
                })

            # Evening Star (bearish reversal)
            if (prev2['type'] == 'bullish' and
                prev['body_size'] < prev2['body_size'] * 0.3 and
                last['type'] == 'bearish' and
                last['body_size'] > prev['body_size']):
                patterns.append({
                    'name': 'Evening Star',
                    'type': 'bearish',
                    'reliability': 0.8
                })

            # Three White Soldiers
            if (prev2['type'] == 'bullish' and
                prev['type'] == 'bullish' and
                last['type'] == 'bullish' and
                last['body_top'] < prev['body_top'] < prev2['body_top']):
                patterns.append({
                    'name': 'Three White Soldiers',
                    'type': 'bullish',
                    'reliability': 0.85
                })

            # Three Black Crows
            if (prev2['type'] == 'bearish' and
                prev['type'] == 'bearish' and
                last['type'] == 'bearish' and
                last['body_bottom'] > prev['body_bottom'] > prev2['body_bottom']):
                patterns.append({
                    'name': 'Three Black Crows',
                    'type': 'bearish',
                    'reliability': 0.85
                })

        return patterns

    # ============================================
    # ===== VOLUME ANALYSIS =====
    # ============================================

    def _analyze_volume(self, img_array):
        """Analyze volume bars if visible at bottom of chart"""
        h, w = img_array.shape[:2]

        # Volume bars usually in bottom 15-20% of chart
        volume_area = img_array[int(h * 0.82):int(h * 0.98), int(w * 0.08):int(w * 0.92)]
        vh, vw = volume_area.shape[:2]

        if vh < 10:
            return {'visible': False, 'trend': 'unknown', 'strength': 0.5}

        # Check for colored bars
        green_count = 0
        red_count = 0
        total = 0

        for y in range(0, vh, 2):
            for x in range(0, vw, 5):
                r, g, b = volume_area[y, x]
                total += 1

                if g > r + 15 and g > b + 10 and g > 40:
                    green_count += 1
                elif r > g + 15 and r > b + 10 and r > 40:
                    red_count += 1

        color_ratio = (green_count + red_count) / total if total > 0 else 0

        if color_ratio < 0.02:
            return {'visible': False, 'trend': 'unknown', 'strength': 0.5}

        # Volume trend
        left_vol = volume_area[:, :vw//2]
        right_vol = volume_area[:, vw//2:]

        left_color = self._count_color_pixels(left_vol, 'green') + self._count_color_pixels(left_vol, 'red')
        right_color = self._count_color_pixels(right_vol, 'green') + self._count_color_pixels(right_vol, 'red')

        if right_color > left_color * 1.3:
            vol_trend = 'increasing'
        elif left_color > right_color * 1.3:
            vol_trend = 'decreasing'
        else:
            vol_trend = 'stable'

        return {
            'visible': True,
            'trend': vol_trend,
            'strength': min(color_ratio * 10, 1.0),
            'green_volume': green_count,
            'red_volume': red_count,
            'buy_pressure': green_count > red_count
        }

    # ============================================
    # ===== INDICATOR DETECTION =====
    # ============================================

    def _detect_indicators(self, img_array):
        """Detect if indicators like MA, RSI, Bollinger Bands are visible"""
        h, w = img_array.shape[:2]
        indicators = {
            'moving_averages': False,
            'rsi': False,
            'bollinger_bands': False,
            'detected_lines': 0
        }

        # Check for smooth curved lines (Moving Averages)
        chart_area = img_array[int(h*0.1):int(h*0.8), int(w*0.1):int(w*0.9)]

        # Look for yellow/blue/orange lines (common MA colors)
        ma_colors = [
            {'r_range': (200, 255), 'g_range': (180, 255), 'b_range': (0, 100)},   # Yellow
            {'r_range': (0, 100), 'g_range': (100, 200), 'b_range': (200, 255)},    # Blue
            {'r_range': (255, 255), 'g_range': (100, 180), 'b_range': (0, 80)},     # Orange
            {'r_range': (200, 255), 'g_range': (0, 100), 'b_range': (200, 255)},    # Purple
            {'r_range': (0, 100), 'g_range': (200, 255), 'b_range': (200, 255)},    # Cyan
        ]

        line_count = 0
        ch, cw = chart_area.shape[:2]

        for color in ma_colors:
            pixel_count = 0
            for y in range(0, ch, 5):
                for x in range(0, cw, 5):
                    r, g, b = chart_area[y, x]

                    if (color['r_range'][0] <= r <= color['r_range'][1] and
                        color['g_range'][0] <= g <= color['g_range'][1] and
                        color['b_range'][0] <= b <= color['b_range'][1]):
                        pixel_count += 1

            total_sampled = (ch // 5) * (cw // 5)
            if total_sampled > 0 and pixel_count / total_sampled > 0.005:
                line_count += 1

        if line_count >= 1:
            indicators['moving_averages'] = True
            indicators['detected_lines'] = line_count

        if line_count >= 2:
            indicators['bollinger_bands'] = True

        # Check for RSI/MACD area (separate panel at bottom)
        bottom_panel = img_array[int(h*0.7):int(h*0.85), :]
        bh, bw = bottom_panel.shape[:2]

        # Check for horizontal line at 0.5 level (RSI 50 line)
        panel_has_indicator = False
        for y in range(0, bh, 3):
            line = bottom_panel[y, :, :]
            unique_colors = len(set([tuple(line[x]) for x in range(0, bw, 10)]))

            if unique_colors > 5:
                panel_has_indicator = True
                break

        if panel_has_indicator:
            indicators['rsi'] = True

        return indicators

    # ============================================
    # ===== VOLATILITY =====
    # ============================================

    def _calculate_volatility(self, candles, img_array):
        """Calculate market volatility from candle sizes"""
        if len(candles) < 3:
            return self._calculate_volatility_from_image(img_array)

        # Use candle body sizes and wick sizes
        body_sizes = [c['body_size'] for c in candles]
        total_sizes = [c['body_size'] + c['upper_wick'] + c['lower_wick'] for c in candles]

        avg_body = np.mean(body_sizes) if body_sizes else 0
        std_body = np.std(body_sizes) if len(body_sizes) > 1 else 0
        avg_total = np.mean(total_sizes) if total_sizes else 0

        # Recent volatility
        recent = candles[-5:] if len(candles) >= 5 else candles
        recent_sizes = [c['body_size'] + c['upper_wick'] + c['lower_wick'] for c in recent]
        recent_avg = np.mean(recent_sizes) if recent_sizes else 0

        # Volatility score (0-1)
        volatility_score = min(avg_total * 20, 1.0)

        # Classify
        if volatility_score > 0.7:
            level = 'high'
        elif volatility_score > 0.4:
            level = 'medium'
        else:
            level = 'low'

        # Check if increasing or decreasing
        if recent_avg > avg_total * 1.3:
            trend = 'increasing'
        elif recent_avg < avg_total * 0.7:
            trend = 'decreasing'
        else:
            trend = 'stable'

        return {
            'level': level,
            'score': volatility_score,
            'trend': trend,
            'avg_body': avg_body,
            'std_body': std_body
        }

    def _calculate_volatility_from_image(self, img_array):
        """Fallback volatility calculation"""
        h, w = img_array.shape[:2]
        chart_area = img_array[int(h*0.1):int(h*0.8), int(w*0.1):int(w*0.9)]

        # Use color variance as proxy for volatility
        variance = np.var(chart_area)
        vol_score = min(variance / 5000, 1.0)

        if vol_score > 0.7:
            level = 'high'
        elif vol_score > 0.4:
            level = 'medium'
        else:
            level = 'low'

        return {
            'level': level,
            'score': vol_score,
            'trend': 'unknown',
            'avg_body': 0,
            'std_body': 0
        }

    # ============================================
    # ===== CONSOLIDATION / BREAKOUT =====
    # ============================================

    def _detect_consolidation(self, candles, img_array):
        """Detect if market is consolidating or breaking out"""
        if len(candles) < 5:
            return {
                'is_consolidating': False,
                'is_breakout': False,
                'breakout_direction': None,
                'range_position': 'middle'
            }

        # Check if recent candles are in a tight range
        recent = candles[-8:] if len(candles) >= 8 else candles
        body_tops = [c['body_top'] for c in recent]
        body_bottoms = [c['body_bottom'] for c in recent]

        price_range = max(body_bottoms) - min(body_tops)
        avg_body = np.mean([c['body_size'] for c in recent])

        is_consolidating = price_range < avg_body * 8

        # Check for breakout (last candle much bigger than average)
        last = candles[-1]
        is_breakout = False
        breakout_direction = None

        if last['body_size'] > avg_body * 2:
            is_breakout = True
            breakout_direction = 'up' if last['type'] == 'bullish' else 'down'

        # Range position
        if len(body_tops) > 0 and len(body_bottoms) > 0:
            range_high = min(body_tops)
            range_low = max(body_bottoms)
            range_size = range_low - range_high

            if range_size > 0:
                last_position = (last['body_bottom'] - range_high) / range_size
                if last_position < 0.3:
                    range_position = 'top'
                elif last_position > 0.7:
                    range_position = 'bottom'
                else:
                    range_position = 'middle'
            else:
                range_position = 'middle'
        else:
            range_position = 'middle'

        return {
            'is_consolidating': is_consolidating,
            'is_breakout': is_breakout,
            'breakout_direction': breakout_direction,
            'range_position': range_position,
            'price_range': price_range
        }

    # ============================================
    # ===== LAST CANDLE ANALYSIS =====
    # ============================================

    def _analyze_last_candle(self, candles, img_array):
        """Deep analysis of the last candle"""
        if not candles:
            return self._analyze_last_candle_from_image(img_array)

        last = candles[-1]

        # Candle characteristics
        is_doji = last['body_size'] < 0.003
        is_hammer = last['lower_wick'] > last['body_size'] * 2.5 and last['upper_wick'] < last['body_size'] * 0.5
        is_shooting_star = last['upper_wick'] > last['body_size'] * 2.5 and last['lower_wick'] < last['body_size'] * 0.5
        is_marubozu = last['upper_wick'] < last['body_size'] * 0.1 and last['lower_wick'] < last['body_size'] * 0.1
        is_strong = last['body_size'] > 0.02

        # Rejection analysis
        total_wick = last['upper_wick'] + last['lower_wick']
        has_rejection = total_wick > last['body_size'] * 2

        if has_rejection:
            if last['upper_wick'] > last['lower_wick']:
                rejection_from = 'top'
            else:
                rejection_from = 'bottom'
        else:
            rejection_from = None

        return {
            'type': last['type'],
            'body_size': last['body_size'],
            'is_doji': is_doji,
            'is_hammer': is_hammer,
            'is_shooting_star': is_shooting_star,
            'is_marubozu': is_marubozu,
            'is_strong': is_strong,
            'has_rejection': has_rejection,
            'rejection_from': rejection_from,
            'upper_wick': last['upper_wick'],
            'lower_wick': last['lower_wick'],
            'color_strength': last.get('color_strength', 0)
        }

    def _analyze_last_candle_from_image(self, img_array):
        """Fallback - analyze rightmost part of image"""
        h, w = img_array.shape[:2]
        right_section = img_array[int(h*0.1):int(h*0.85), int(w*0.85):int(w*0.95)]

        green = self._count_color_pixels(right_section, 'green')
        red = self._count_color_pixels(right_section, 'red')

        candle_type = 'bullish' if green > red else 'bearish' if red > green else 'neutral'

        return {
            'type': candle_type,
            'body_size': 0,
            'is_doji': candle_type == 'neutral',
            'is_hammer': False,
            'is_shooting_star': False,
            'is_marubozu': False,
            'is_strong': False,
            'has_rejection': False,
            'rejection_from': None,
            'upper_wick': 0,
            'lower_wick': 0,
            'color_strength': 0
        }

    # ============================================
    # ===== COLOR RATIO ANALYSIS =====
    # ============================================

    def _analyze_color_ratio(self, img_array):
        """Analyze overall green vs red ratio in chart"""
        h, w = img_array.shape[:2]

        # Focus on chart area
        chart = img_array[int(h*0.05):int(h*0.85), int(w*0.08):int(w*0.92)]

        total_green = 0
        total_red = 0
        total_sampled = 0

        ch, cw = chart.shape[:2]

        for y in range(0, ch, 4):
            for x in range(0, cw, 4):
                r, g, b = chart[y, x]
                total_sampled += 1

                if g > r + 20 and g > b + 15 and g > 50:
                    total_green += 1
                elif r > g + 20 and r > b + 15 and r > 50:
                    total_red += 1

        total_color = total_green + total_red
        if total_color == 0:
            return {
                'green_ratio': 0.5,
                'red_ratio': 0.5,
                'dominant': 'neutral',
                'strength': 0
            }

        green_ratio = total_green / total_color
        red_ratio = total_red / total_color

        if green_ratio > 0.6:
            dominant = 'bullish'
        elif red_ratio > 0.6:
            dominant = 'bearish'
        else:
            dominant = 'neutral'

        strength = abs(green_ratio - red_ratio)

        return {
            'green_ratio': round(green_ratio, 3),
            'red_ratio': round(red_ratio, 3),
            'dominant': dominant,
            'strength': round(strength, 3)
        }

    # ============================================
    # ===== MOMENTUM ANALYSIS =====
    # ============================================

    def _analyze_momentum(self, candles, img_array):
        """Analyze market momentum"""
        if len(candles) < 3:
            return {
                'direction': 'neutral',
                'strength': 0.5,
                'is_exhausted': False,
                'continuous_count': 0
            }

        # Count consecutive same-direction candles
        last_type = candles[-1]['type']
        continuous = 1

        for i in range(len(candles) - 2, -1, -1):
            if candles[i]['type'] == last_type:
                continuous += 1
            else:
                break

        # Check if momentum is exhausting
        is_exhausted = False
        if continuous >= 4:
            # Check if bodies are getting smaller
            recent_bodies = [candles[-(i+1)]['body_size'] for i in range(min(continuous, 5))]
            if len(recent_bodies) >= 3:
                if recent_bodies[0] < recent_bodies[-1] * 0.5:
                    is_exhausted = True

        # Momentum strength
        recent_5 = candles[-5:] if len(candles) >= 5 else candles
        bullish_bodies = sum(c['body_size'] for c in recent_5 if c['type'] == 'bullish')
        bearish_bodies = sum(c['body_size'] for c in recent_5 if c['type'] == 'bearish')

        total_body = bullish_bodies + bearish_bodies
        if total_body > 0:
            if bullish_bodies > bearish_bodies:
                strength = bullish_bodies / total_body
                direction = 'bullish'
            else:
                strength = bearish_bodies / total_body
                direction = 'bearish'
        else:
            strength = 0.5
            direction = 'neutral'

        return {
            'direction': direction,
            'strength': round(strength, 3),
            'is_exhausted': is_exhausted,
            'continuous_count': continuous,
            'last_type': last_type
        }

    # ============================================
    # ===== PRICE ACTION =====
    # ============================================

    def _analyze_price_action(self, candles, img_array):
        """Comprehensive price action analysis"""
        if len(candles) < 2:
            return {
                'trend_strength': 0.5,
                'pullback': False,
                'reversal_signal': False,
                'continuation': False,
                'fake_breakout': False,
                'liquidity_grab': False
            }

        last = candles[-1]
        prev = candles[-2]

        # Pullback detection
        trend = self._detect_trend(candles[:-2], img_array) if len(candles) > 4 else None
        pullback = False

        if trend and len(candles) > 4:
            if trend['direction'] == 'uptrend' and last['type'] == 'bearish':
                pullback = True
            elif trend['direction'] == 'downtrend' and last['type'] == 'bullish':
                pullback = True

        # Reversal signal
        reversal_signal = False
        if (prev['type'] != last['type'] and
            last['body_size'] > prev['body_size'] * 1.5):
            reversal_signal = True

        # Continuation
        continuation = False
        if len(candles) >= 3:
            if (candles[-3]['type'] == candles[-2]['type'] == candles[-1]['type']):
                continuation = True

        # Fake breakout detection
        fake_breakout = False
        if last['has_rejection'] if hasattr(last, 'has_rejection') else False:
            if last['upper_wick'] > last['body_size'] * 3:
                fake_breakout = True
            elif last['lower_wick'] > last['body_size'] * 3:
                fake_breakout = True

        # Liquidity grab
        liquidity_grab = False
        if len(candles) >= 5:
            recent_highs = [c['body_top'] for c in candles[-5:-1]]
            recent_lows = [c['body_bottom'] for c in candles[-5:-1]]

            # Last candle exceeded previous highs/lows but reversed
            if (last['upper_wick'] > 0 and
                min(last['body_top'] - last['upper_wick'], last['body_top']) < min(recent_highs) and
                last['type'] == 'bearish'):
                liquidity_grab = True

            if (last['lower_wick'] > 0 and
                max(last['body_bottom'] + last['lower_wick'], last['body_bottom']) > max(recent_lows) and
                last['type'] == 'bullish'):
                liquidity_grab = True

        return {
            'trend_strength': trend['strength'] if trend else 0.5,
            'pullback': pullback,
            'reversal_signal': reversal_signal,
            'continuation': continuation,
            'fake_breakout': fake_breakout,
            'liquidity_grab': liquidity_grab
        }

    # ============================================
    # ===== DEFAULT DATA =====
    # ============================================

    def _default_chart_data(self):
        """Return default data when analysis fails"""
        return {
            'candles': [],
            'trend': {'direction': 'sideways', 'strength': 0.3, 'bullish_count': 0, 'bearish_count': 0},
            'structure': {'type': 'unclear', 'strength': 0.3, 'higher_highs': False, 'higher_lows': False, 'lower_highs': False, 'lower_lows': False},
            'support_resistance': {'support_levels': [], 'resistance_levels': [], 'near_support': False, 'near_resistance': False, 'at_level': None},
            'patterns': [],
            'volume': {'visible': False, 'trend': 'unknown', 'strength': 0.5},
            'indicators': {'moving_averages': False, 'rsi': False, 'bollinger_bands': False, 'detected_lines': 0},
            'volatility': {'level': 'medium', 'score': 0.5, 'trend': 'unknown'},
            'consolidation': {'is_consolidating': False, 'is_breakout': False, 'breakout_direction': None, 'range_position': 'middle'},
            'last_candle': {'type': 'neutral', 'body_size': 0, 'is_doji': True, 'is_hammer': False, 'is_shooting_star': False, 'is_marubozu': False, 'is_strong': False, 'has_rejection': False, 'rejection_from': None},
            'color_analysis': {'green_ratio': 0.5, 'red_ratio': 0.5, 'dominant': 'neutral', 'strength': 0},
            'momentum': {'direction': 'neutral', 'strength': 0.5, 'is_exhausted': False, 'continuous_count': 0},
            'price_action': {'trend_strength': 0.5, 'pullback': False, 'reversal_signal': False, 'continuation': False, 'fake_breakout': False, 'liquidity_grab': False},
            'image_size': (0, 0)
        }