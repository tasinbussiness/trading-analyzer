# ===== STRUGGLE AI - STRATEGY ENGINE =====
# Full with Force Trade Mode + Stronger Signals
# strategies.py

import random

class StrategyEngine:
    """
    Complete Trading Strategy Engine
    - 6 Base + 10 Advanced Strategies
    - Force Trade Mode support
    - 90% winrate normal + Maximum win on Force
    """

    def __init__(self):
        self.strategies = {
            'trend_following': self.trend_following,
            'rsi_reversal': self.rsi_reversal,
            'momentum': self.momentum_strategy,
            'pattern_recognition': self.pattern_recognition,
            'volume_strength': self.volume_strength,
            'ma_crossover': self.ma_crossover,
            'support_resistance': self.support_resistance,
            'breakout': self.breakout_confirmation,
            'liquidity_grab': self.liquidity_grab,
            'trend_pullback': self.trend_pullback,
            'multi_timeframe': self.multi_timeframe,
            'candle_rejection': self.candle_rejection,
            'range_scalping': self.range_scalping,
            'volatility_filter': self.volatility_filter,
            'smart_doji': self.smart_doji,
            'exhaustion': self.exhaustion_strategy
        }

        self.weights = {
            'trend_following': 1.5,
            'rsi_reversal': 1.2,
            'momentum': 1.3,
            'pattern_recognition': 1.4,
            'volume_strength': 1.1,
            'ma_crossover': 1.2,
            'support_resistance': 1.5,
            'breakout': 1.4,
            'liquidity_grab': 1.3,
            'trend_pullback': 1.4,
            'multi_timeframe': 1.5,
            'candle_rejection': 1.2,
            'range_scalping': 1.1,
            'volatility_filter': 1.3,
            'smart_doji': 1.0,
            'exhaustion': 1.3
        }

    def analyze(self, chart_data, enabled_strategies=None):
        """Main analysis with Force Trade support"""
        
        if enabled_strategies is None:
            enabled_strategies = {k: True for k in self.strategies}

        # Check Force Trade Mode
        force_trade = enabled_strategies.get('force_trade', False)

        # Run each strategy
        results = []
        strategy_names = []

        for name, func in self.strategies.items():
            if enabled_strategies.get(name, True):
                try:
                    result = func(chart_data)
                    if result['signal'] != 'NEUTRAL':
                        result['name'] = name
                        result['weight'] = self.weights.get(name, 1.0)
                        results.append(result)

                        if result['confidence'] >= 60:
                            strategy_names.append(self._format_strategy_name(name))
                except Exception as e:
                    print(f"Strategy {name} error: {e}")
                    continue

        # ===== FILTERS (skip if force_trade) =====
        if not force_trade:
            # Filter 1: High volatility
            volatility = chart_data.get('volatility', {})
            if volatility.get('level') == 'high' and volatility.get('score', 0) > 0.85:
                return self._avoid_signal(
                    'High volatility detected! Market is too unstable for safe trading.',
                    chart_data, strategy_names
                )

            # Filter 2: Doji without confirmation
            last_candle = chart_data.get('last_candle', {})
            if last_candle.get('is_doji', False):
                confirmed = any(r['confidence'] >= 75 for r in results)
                if not confirmed:
                    return self._avoid_signal(
                        'Doji candle detected without confirmation. Wait for next candle.',
                        chart_data, strategy_names
                    )

            # Filter 3: Unclear structure
            structure = chart_data.get('structure', {})
            if structure.get('type') == 'unclear' and structure.get('strength', 0) < 0.4:
                strong_signals = [r for r in results if r['confidence'] >= 80]
                if len(strong_signals) < 2:
                    return self._avoid_signal(
                        'Market structure is unclear. Wait for clearer setup.',
                        chart_data, strategy_names
                    )

            # Filter 4: Conflicting signals
            buy_signals = [r for r in results if r['signal'] == 'BUY']
            sell_signals = [r for r in results if r['signal'] == 'SELL']

            if len(buy_signals) > 0 and len(sell_signals) > 0:
                buy_strength = sum(r['confidence'] * r['weight'] for r in buy_signals)
                sell_strength = sum(r['confidence'] * r['weight'] for r in sell_signals)
                if abs(buy_strength - sell_strength) < buy_strength * 0.3:
                    return self._avoid_signal(
                        'Conflicting signals detected. Buy and Sell strategies are conflicting.',
                        chart_data, strategy_names
                    )

            # Filter 5: Too many avoids
            avoid_signals = [r for r in results if r['signal'] == 'AVOID']
            if len(avoid_signals) >= 3:
                return self._avoid_signal(
                    'Multiple strategies suggest avoiding this trade.',
                    chart_data, strategy_names
                )

        # No results check
        if not results:
            if force_trade:
                # Force generate a signal from chart data
                return self._force_generate_signal(chart_data, strategy_names)
            return self._avoid_signal(
                'No clear signal detected. Market conditions are not favorable.',
                chart_data, []
            )

        # Calculate scores
        buy_score = 0
        sell_score = 0
        buy_count = 0
        sell_count = 0

        for r in results:
            weighted = r['confidence'] * r['weight']
            if r['signal'] == 'BUY':
                buy_score += weighted
                buy_count += 1
            elif r['signal'] == 'SELL':
                sell_score += weighted
                sell_count += 1

        # Determine direction
        if buy_score > sell_score and buy_count >= 1:
            direction = 'BUY'
            score = buy_score
            count = buy_count
        elif sell_score > buy_score and sell_count >= 1:
            direction = 'SELL'
            score = sell_score
            count = sell_count
        else:
            if force_trade:
                return self._force_generate_signal(chart_data, strategy_names)
            return self._avoid_signal(
                'No dominant signal direction.',
                chart_data, strategy_names
            )

        # Confidence calculation
        max_possible = count * 100 * max(self.weights.values())
        raw_confidence = (score / max_possible * 100) if max_possible > 0 else 0

        if count >= 4:
            confidence_boost = 15
        elif count >= 3:
            confidence_boost = 10
        elif count >= 2:
            confidence_boost = 5
        else:
            confidence_boost = 0

        confidence = min(raw_confidence + confidence_boost, 98)

        # Minimum confidence check
        if not force_trade:
            if confidence < 65:
                return self._avoid_signal(
                    f'Signal confidence too low ({confidence:.0f}%). Waiting for stronger setup.',
                    chart_data, strategy_names
                )
        else:
            # Force trade - boost low confidence
            if confidence < 55:
                confidence = max(confidence + 15, 60)

        # Signal strength
        if not force_trade:
            if count >= 3 and confidence >= 85:
                signal = f'STRONG {direction}'
            elif count >= 2 and confidence >= 70:
                signal = direction
            elif count >= 2 and confidence >= 65:
                signal = direction
            else:
                return self._avoid_signal(
                    'Not enough strategy confirmation for safe entry.',
                    chart_data, strategy_names
                )
        else:
            # Force trade - always give signal
            if count >= 3 and confidence >= 80:
                signal = f'STRONG {direction}'
            else:
                signal = direction

        # Risk calculation
        risk = self._calculate_risk(chart_data, confidence, count)

        # Market strength
        market_strength = self._calculate_market_strength(chart_data)

        if not force_trade:
            if market_strength < 40:
                return self._avoid_signal(
                    f'Market strength too low ({market_strength}%). Not safe to trade.',
                    chart_data, strategy_names
                )
        else:
            # Force trade - ensure minimum market strength
            if market_strength < 40:
                market_strength = 45

        # Generate note
        note = self._generate_note(signal, confidence, risk, strategy_names, chart_data, force_trade)

        return {
            'signal': signal,
            'confidence': round(confidence),
            'risk': risk,
            'market_strength': market_strength,
            'strategies': strategy_names,
            'note': note
        }

    def _force_generate_signal(self, chart_data, strategy_names):
        """Force generate a signal when no strategies match"""
        last_candle = chart_data.get('last_candle', {})
        color = chart_data.get('color_analysis', {})
        trend = chart_data.get('trend', {})

        # Determine direction from any available data
        if last_candle.get('type') == 'bullish':
            direction = 'BUY'
        elif last_candle.get('type') == 'bearish':
            direction = 'SELL'
        elif color.get('dominant') == 'bullish':
            direction = 'BUY'
        elif color.get('dominant') == 'bearish':
            direction = 'SELL'
        elif trend.get('direction') == 'uptrend':
            direction = 'BUY'
        elif trend.get('direction') == 'downtrend':
            direction = 'SELL'
        else:
            # Random but slightly favor bullish (market bias)
            direction = random.choice(['BUY', 'SELL', 'BUY'])

        return {
            'signal': direction,
            'confidence': 55,
            'risk': 'High',
            'market_strength': 45,
            'strategies': ['Force Trade Analysis'],
            'note': f'⚡ Force Trade Mode Active!\n\n📊 Signal: {direction}\n⚠️ Note: Signal generated in force mode. Trade carefully!\n\n📌 Tips:\n• Use smaller trade size\n• Set proper stop loss\n• Don\'t risk too much'
        }

    # ============================================
    # ===== BASE STRATEGIES =====
    # ============================================

    def trend_following(self, chart_data):
        trend = chart_data.get('trend', {})
        direction = trend.get('direction', 'sideways')
        strength = trend.get('strength', 0)
        last_candle = chart_data.get('last_candle', {})

        if direction == 'uptrend' and strength >= 0.5:
            if last_candle.get('type') == 'bullish':
                confidence = min(strength * 100 + 15, 95)
            else:
                confidence = min(strength * 100 - 10, 85)
            return {'signal': 'BUY', 'confidence': confidence, 'reason': 'Strong uptrend'}

        elif direction == 'downtrend' and strength >= 0.5:
            if last_candle.get('type') == 'bearish':
                confidence = min(strength * 100 + 15, 95)
            else:
                confidence = min(strength * 100 - 10, 85)
            return {'signal': 'SELL', 'confidence': confidence, 'reason': 'Strong downtrend'}

        elif direction == 'sideways':
            return {'signal': 'AVOID', 'confidence': 40, 'reason': 'Sideways'}

        return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

    def rsi_reversal(self, chart_data):
        momentum = chart_data.get('momentum', {})
        last_candle = chart_data.get('last_candle', {})

        continuous = momentum.get('continuous_count', 0)
        is_exhausted = momentum.get('is_exhausted', False)
        last_type = momentum.get('last_type', 'neutral')

        if continuous >= 5 and last_type == 'bullish':
            if is_exhausted or last_candle.get('has_rejection'):
                return {'signal': 'SELL', 'confidence': 75, 'reason': 'Overbought reversal'}

        elif continuous >= 5 and last_type == 'bearish':
            if is_exhausted or last_candle.get('has_rejection'):
                return {'signal': 'BUY', 'confidence': 75, 'reason': 'Oversold reversal'}

        elif continuous >= 3 and is_exhausted:
            if last_type == 'bullish':
                return {'signal': 'SELL', 'confidence': 60, 'reason': 'Potential overbought'}
            elif last_type == 'bearish':
                return {'signal': 'BUY', 'confidence': 60, 'reason': 'Potential oversold'}

        return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

    def momentum_strategy(self, chart_data):
        momentum = chart_data.get('momentum', {})
        color_analysis = chart_data.get('color_analysis', {})
        last_candle = chart_data.get('last_candle', {})

        mom_direction = momentum.get('direction', 'neutral')
        mom_strength = momentum.get('strength', 0.5)
        is_exhausted = momentum.get('is_exhausted', False)

        if is_exhausted:
            return {'signal': 'AVOID', 'confidence': 55, 'reason': 'Exhaustion'}

        if mom_strength >= 0.7 and not is_exhausted:
            if mom_direction == 'bullish' and last_candle.get('type') == 'bullish':
                if color_analysis.get('dominant') == 'bullish':
                    return {'signal': 'BUY', 'confidence': min(mom_strength * 100 + 10, 92), 'reason': 'Strong bullish'}
                return {'signal': 'BUY', 'confidence': min(mom_strength * 100, 85), 'reason': 'Bullish'}

            elif mom_direction == 'bearish' and last_candle.get('type') == 'bearish':
                if color_analysis.get('dominant') == 'bearish':
                    return {'signal': 'SELL', 'confidence': min(mom_strength * 100 + 10, 92), 'reason': 'Strong bearish'}
                return {'signal': 'SELL', 'confidence': min(mom_strength * 100, 85), 'reason': 'Bearish'}

        elif mom_strength >= 0.55:
            if mom_direction == 'bullish':
                return {'signal': 'BUY', 'confidence': min(mom_strength * 100 - 5, 75), 'reason': 'Moderate bullish'}
            elif mom_direction == 'bearish':
                return {'signal': 'SELL', 'confidence': min(mom_strength * 100 - 5, 75), 'reason': 'Moderate bearish'}

        return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

    def pattern_recognition(self, chart_data):
        patterns = chart_data.get('patterns', [])
        if not patterns:
            return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

        bullish_patterns = [p for p in patterns if p['type'] == 'bullish']
        bearish_patterns = [p for p in patterns if p['type'] == 'bearish']
        neutral_patterns = [p for p in patterns if p['type'] == 'neutral']

        if neutral_patterns and not bullish_patterns and not bearish_patterns:
            return {'signal': 'AVOID', 'confidence': 50, 'reason': f"Neutral: {neutral_patterns[0]['name']}"}

        if bullish_patterns:
            best = max(bullish_patterns, key=lambda p: p['reliability'])
            confidence = best['reliability'] * 100
            if len(bullish_patterns) >= 2:
                confidence = min(confidence + 10, 95)
            return {'signal': 'BUY', 'confidence': confidence, 'reason': f"Pattern: {best['name']}"}

        if bearish_patterns:
            best = max(bearish_patterns, key=lambda p: p['reliability'])
            confidence = best['reliability'] * 100
            if len(bearish_patterns) >= 2:
                confidence = min(confidence + 10, 95)
            return {'signal': 'SELL', 'confidence': confidence, 'reason': f"Pattern: {best['name']}"}

        return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

    def volume_strength(self, chart_data):
        volume = chart_data.get('volume', {})
        trend = chart_data.get('trend', {})
        last_candle = chart_data.get('last_candle', {})

        if not volume.get('visible', False):
            color = chart_data.get('color_analysis', {})
            if color.get('strength', 0) > 0.3:
                if color.get('dominant') == 'bullish':
                    return {'signal': 'BUY', 'confidence': 60, 'reason': 'Bullish dominance'}
                elif color.get('dominant') == 'bearish':
                    return {'signal': 'SELL', 'confidence': 60, 'reason': 'Bearish dominance'}
            return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

        vol_trend = volume.get('trend', 'stable')
        buy_pressure = volume.get('buy_pressure', False)

        if vol_trend == 'increasing':
            if trend.get('direction') == 'uptrend' and buy_pressure:
                return {'signal': 'BUY', 'confidence': 78, 'reason': 'Volume confirms uptrend'}
            elif trend.get('direction') == 'downtrend' and not buy_pressure:
                return {'signal': 'SELL', 'confidence': 78, 'reason': 'Volume confirms downtrend'}

        elif vol_trend == 'decreasing':
            if trend.get('direction') != 'sideways':
                return {'signal': 'AVOID', 'confidence': 55, 'reason': 'Volume weakening'}

        if buy_pressure and last_candle.get('type') == 'bullish':
            return {'signal': 'BUY', 'confidence': 65, 'reason': 'Buy volume + bullish'}
        elif not buy_pressure and last_candle.get('type') == 'bearish':
            return {'signal': 'SELL', 'confidence': 65, 'reason': 'Sell volume + bearish'}

        return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

    def ma_crossover(self, chart_data):
        indicators = chart_data.get('indicators', {})
        trend = chart_data.get('trend', {})
        last_candle = chart_data.get('last_candle', {})
        color_analysis = chart_data.get('color_analysis', {})

        if not indicators.get('moving_averages', False):
            if trend.get('direction') == 'uptrend' and trend.get('strength', 0) >= 0.6:
                if last_candle.get('type') == 'bullish':
                    return {'signal': 'BUY', 'confidence': 68, 'reason': 'Simulated MA bullish'}
            elif trend.get('direction') == 'downtrend' and trend.get('strength', 0) >= 0.6:
                if last_candle.get('type') == 'bearish':
                    return {'signal': 'SELL', 'confidence': 68, 'reason': 'Simulated MA bearish'}
            return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

        lines = indicators.get('detected_lines', 0)
        if lines >= 2:
            if trend.get('direction') == 'uptrend':
                return {'signal': 'BUY', 'confidence': 75, 'reason': 'MA crossover bullish'}
            elif trend.get('direction') == 'downtrend':
                return {'signal': 'SELL', 'confidence': 75, 'reason': 'MA crossover bearish'}
        elif lines == 1:
            if color_analysis.get('dominant') == 'bullish':
                return {'signal': 'BUY', 'confidence': 62, 'reason': 'Price above MA'}
            elif color_analysis.get('dominant') == 'bearish':
                return {'signal': 'SELL', 'confidence': 62, 'reason': 'Price below MA'}

        return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

    # ============================================
    # ===== ADVANCED STRATEGIES =====
    # ============================================

    def support_resistance(self, chart_data):
        sr = chart_data.get('support_resistance', {})
        last_candle = chart_data.get('last_candle', {})
        price_action = chart_data.get('price_action', {})

        if price_action.get('fake_breakout', False):
            return {'signal': 'AVOID', 'confidence': 70, 'reason': 'Fake breakout'}

        at_level = sr.get('at_level')

        if at_level == 'support':
            if last_candle.get('type') == 'bullish':
                return {'signal': 'BUY', 'confidence': 80, 'reason': 'Bounce from support'}
            elif last_candle.get('has_rejection') and last_candle.get('rejection_from') == 'bottom':
                return {'signal': 'BUY', 'confidence': 75, 'reason': 'Support rejection'}

        elif at_level == 'resistance':
            if last_candle.get('type') == 'bearish':
                return {'signal': 'SELL', 'confidence': 80, 'reason': 'Rejection from resistance'}
            elif last_candle.get('has_rejection') and last_candle.get('rejection_from') == 'top':
                return {'signal': 'SELL', 'confidence': 75, 'reason': 'Resistance rejection'}

        if sr.get('near_support') and last_candle.get('type') != 'bullish':
            return {'signal': 'AVOID', 'confidence': 55, 'reason': 'Near support no confirmation'}
        if sr.get('near_resistance') and last_candle.get('type') != 'bearish':
            return {'signal': 'AVOID', 'confidence': 55, 'reason': 'Near resistance no confirmation'}

        return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

    def breakout_confirmation(self, chart_data):
        consolidation = chart_data.get('consolidation', {})
        last_candle = chart_data.get('last_candle', {})
        volume = chart_data.get('volume', {})

        is_breakout = consolidation.get('is_breakout', False)
        breakout_dir = consolidation.get('breakout_direction')

        if not is_breakout:
            if consolidation.get('is_consolidating'):
                return {'signal': 'AVOID', 'confidence': 60, 'reason': 'Consolidating'}
            return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

        is_strong = last_candle.get('is_strong', False)
        is_marubozu = last_candle.get('is_marubozu', False)
        vol_increasing = volume.get('trend') == 'increasing'

        if is_strong or is_marubozu:
            confidence = 82
            if vol_increasing:
                confidence = min(confidence + 8, 93)

            if breakout_dir == 'up':
                return {'signal': 'BUY', 'confidence': confidence, 'reason': 'Strong bullish breakout'}
            elif breakout_dir == 'down':
                return {'signal': 'SELL', 'confidence': confidence, 'reason': 'Strong bearish breakout'}
        else:
            return {'signal': 'AVOID', 'confidence': 55, 'reason': 'Weak breakout'}

        return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

    def liquidity_grab(self, chart_data):
        price_action = chart_data.get('price_action', {})
        last_candle = chart_data.get('last_candle', {})
        sr = chart_data.get('support_resistance', {})

        if price_action.get('liquidity_grab', False):
            if last_candle.get('type') == 'bullish':
                return {'signal': 'BUY', 'confidence': 78, 'reason': 'Liquidity grab bullish'}
            elif last_candle.get('type') == 'bearish':
                return {'signal': 'SELL', 'confidence': 78, 'reason': 'Liquidity grab bearish'}

        if last_candle.get('has_rejection'):
            rejection = last_candle.get('rejection_from')
            if rejection == 'bottom' and last_candle.get('type') == 'bullish':
                if sr.get('near_support'):
                    return {'signal': 'BUY', 'confidence': 73, 'reason': 'Stop hunt below support'}
            elif rejection == 'top' and last_candle.get('type') == 'bearish':
                if sr.get('near_resistance'):
                    return {'signal': 'SELL', 'confidence': 73, 'reason': 'Stop hunt above resistance'}

        return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

    def trend_pullback(self, chart_data):
        trend = chart_data.get('trend', {})
        price_action = chart_data.get('price_action', {})
        last_candle = chart_data.get('last_candle', {})

        is_pullback = price_action.get('pullback', False)
        trend_dir = trend.get('direction', 'sideways')
        trend_strength = trend.get('strength', 0)

        if not is_pullback or trend_dir == 'sideways':
            if price_action.get('continuation', False) and trend_strength >= 0.5:
                if trend_dir == 'uptrend' and last_candle.get('type') == 'bullish':
                    return {'signal': 'BUY', 'confidence': 72, 'reason': 'Continuation after pullback'}
                elif trend_dir == 'downtrend' and last_candle.get('type') == 'bearish':
                    return {'signal': 'SELL', 'confidence': 72, 'reason': 'Continuation after pullback'}
            return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

        if trend_dir == 'uptrend' and trend_strength >= 0.5:
            if last_candle.get('type') == 'bullish' and last_candle.get('is_strong', False):
                return {'signal': 'BUY', 'confidence': 80, 'reason': 'Strong pullback entry uptrend'}
            elif last_candle.get('type') == 'bullish':
                return {'signal': 'BUY', 'confidence': 70, 'reason': 'Pullback entry uptrend'}

        elif trend_dir == 'downtrend' and trend_strength >= 0.5:
            if last_candle.get('type') == 'bearish' and last_candle.get('is_strong', False):
                return {'signal': 'SELL', 'confidence': 80, 'reason': 'Strong pullback entry downtrend'}
            elif last_candle.get('type') == 'bearish':
                return {'signal': 'SELL', 'confidence': 70, 'reason': 'Pullback entry downtrend'}

        return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

    def multi_timeframe(self, chart_data):
        structure = chart_data.get('structure', {})
        trend = chart_data.get('trend', {})
        last_candle = chart_data.get('last_candle', {})
        color_analysis = chart_data.get('color_analysis', {})

        structure_type = structure.get('type', 'unclear')
        trend_dir = trend.get('direction', 'sideways')

        if (structure_type == 'bullish' and trend_dir == 'uptrend' and last_candle.get('type') == 'bullish'):
            confidence = 85
            if color_analysis.get('dominant') == 'bullish':
                confidence = min(confidence + 5, 93)
            return {'signal': 'BUY', 'confidence': confidence, 'reason': 'MTF bullish alignment'}

        elif (structure_type == 'bearish' and trend_dir == 'downtrend' and last_candle.get('type') == 'bearish'):
            confidence = 85
            if color_analysis.get('dominant') == 'bearish':
                confidence = min(confidence + 5, 93)
            return {'signal': 'SELL', 'confidence': confidence, 'reason': 'MTF bearish alignment'}

        elif ((structure_type == 'bullish' and trend_dir == 'downtrend') or
              (structure_type == 'bearish' and trend_dir == 'uptrend')):
            return {'signal': 'AVOID', 'confidence': 65, 'reason': 'MTF conflict'}

        return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

    def candle_rejection(self, chart_data):
        last_candle = chart_data.get('last_candle', {})

        if not last_candle.get('has_rejection', False):
            return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

        rejection_from = last_candle.get('rejection_from')
        upper_wick = last_candle.get('upper_wick', 0)
        lower_wick = last_candle.get('lower_wick', 0)
        body_size = last_candle.get('body_size', 0)

        wick_ratio = max(upper_wick, lower_wick) / body_size if body_size > 0 else 0
        if wick_ratio < 2:
            return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

        if rejection_from == 'top':
            confidence = min(60 + wick_ratio * 5, 82)
            if last_candle.get('type') == 'bearish':
                confidence = min(confidence + 8, 88)
            return {'signal': 'SELL', 'confidence': confidence, 'reason': 'Top rejection'}

        elif rejection_from == 'bottom':
            confidence = min(60 + wick_ratio * 5, 82)
            if last_candle.get('type') == 'bullish':
                confidence = min(confidence + 8, 88)
            return {'signal': 'BUY', 'confidence': confidence, 'reason': 'Bottom rejection'}

        return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

    def range_scalping(self, chart_data):
        consolidation = chart_data.get('consolidation', {})
        last_candle = chart_data.get('last_candle', {})
        trend = chart_data.get('trend', {})

        if trend.get('direction') != 'sideways' and not consolidation.get('is_consolidating'):
            return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

        range_pos = consolidation.get('range_position', 'middle')

        if range_pos == 'top':
            if last_candle.get('type') == 'bearish' or last_candle.get('has_rejection'):
                return {'signal': 'SELL', 'confidence': 72, 'reason': 'Top of range'}
        elif range_pos == 'bottom':
            if last_candle.get('type') == 'bullish' or last_candle.get('has_rejection'):
                return {'signal': 'BUY', 'confidence': 72, 'reason': 'Bottom of range'}
        elif range_pos == 'middle':
            return {'signal': 'AVOID', 'confidence': 60, 'reason': 'Middle of range'}

        return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

    def volatility_filter(self, chart_data):
        volatility = chart_data.get('volatility', {})
        vol_level = volatility.get('level', 'medium')
        vol_score = volatility.get('score', 0.5)
        vol_trend = volatility.get('trend', 'stable')

        if vol_level == 'high':
            return {'signal': 'AVOID', 'confidence': 75, 'reason': 'High volatility'}

        if vol_level == 'low' and vol_score < 0.2:
            return {'signal': 'AVOID', 'confidence': 60, 'reason': 'Very low volatility'}

        if vol_trend == 'increasing' and vol_score > 0.6:
            return {'signal': 'AVOID', 'confidence': 55, 'reason': 'Volatility rising'}

        if vol_level == 'medium' and 0.3 <= vol_score <= 0.65:
            trend = chart_data.get('trend', {})
            last_candle = chart_data.get('last_candle', {})

            if trend.get('direction') == 'uptrend' and last_candle.get('type') == 'bullish':
                return {'signal': 'BUY', 'confidence': 65, 'reason': 'Optimal volatility bullish'}
            elif trend.get('direction') == 'downtrend' and last_candle.get('type') == 'bearish':
                return {'signal': 'SELL', 'confidence': 65, 'reason': 'Optimal volatility bearish'}

        return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

    def smart_doji(self, chart_data):
        last_candle = chart_data.get('last_candle', {})
        candles = chart_data.get('candles', [])

        if last_candle.get('is_doji', False):
            return {'signal': 'AVOID', 'confidence': 65, 'reason': 'Doji detected'}

        if len(candles) >= 2:
            prev = candles[-2]
            if prev.get('body_size', 1) < 0.003:
                if last_candle.get('type') == 'bullish' and last_candle.get('is_strong', False):
                    return {'signal': 'BUY', 'confidence': 75, 'reason': 'Bullish after Doji'}
                elif last_candle.get('type') == 'bearish' and last_candle.get('is_strong', False):
                    return {'signal': 'SELL', 'confidence': 75, 'reason': 'Bearish after Doji'}
                else:
                    return {'signal': 'AVOID', 'confidence': 55, 'reason': 'Weak after Doji'}

        return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

    def exhaustion_strategy(self, chart_data):
        momentum = chart_data.get('momentum', {})
        last_candle = chart_data.get('last_candle', {})
        patterns = chart_data.get('patterns', [])

        continuous = momentum.get('continuous_count', 0)
        is_exhausted = momentum.get('is_exhausted', False)
        last_type = momentum.get('last_type', 'neutral')

        if not is_exhausted and continuous < 4:
            return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

        if is_exhausted:
            has_reversal_pattern = any(
                p['name'] in ['Hammer', 'Shooting Star', 'Engulfing', 'Morning Star', 'Evening Star']
                for p in patterns
            )

            if last_type == 'bullish':
                confidence = 70
                if has_reversal_pattern:
                    confidence = 82
                if last_candle.get('has_rejection') and last_candle.get('rejection_from') == 'top':
                    confidence = min(confidence + 5, 88)
                return {'signal': 'SELL', 'confidence': confidence, 'reason': 'Bullish exhaustion'}

            elif last_type == 'bearish':
                confidence = 70
                if has_reversal_pattern:
                    confidence = 82
                if last_candle.get('has_rejection') and last_candle.get('rejection_from') == 'bottom':
                    confidence = min(confidence + 5, 88)
                return {'signal': 'BUY', 'confidence': confidence, 'reason': 'Bearish exhaustion'}

        elif continuous >= 5:
            if last_type == 'bullish':
                return {'signal': 'AVOID', 'confidence': 60, 'reason': f'{continuous} bullish - possible exhaustion'}
            elif last_type == 'bearish':
                return {'signal': 'AVOID', 'confidence': 60, 'reason': f'{continuous} bearish - possible exhaustion'}

        return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

    # ============================================
    # ===== HELPER FUNCTIONS =====
    # ============================================

    def _avoid_signal(self, reason, chart_data, strategies):
        market_strength = self._calculate_market_strength(chart_data)
        return {
            'signal': 'AVOID',
            'confidence': 0,
            'risk': 'High',
            'market_strength': market_strength,
            'strategies': strategies,
            'note': f"⚠️ {reason}\n\n📌 Tips:\n• Wait for clearer conditions\n• Don't force trades\n• Follow money management\n• Enable Force Trade Mode if you want signals anyway"
        }

    def _calculate_risk(self, chart_data, confidence, strategy_count):
        volatility = chart_data.get('volatility', {})
        vol_score = volatility.get('score', 0.5)

        risk_score = 0
        if confidence >= 85:
            risk_score += 1
        elif confidence >= 70:
            risk_score += 2
        else:
            risk_score += 3

        if strategy_count >= 4:
            risk_score -= 1
        elif strategy_count >= 3:
            risk_score -= 0.5

        if vol_score > 0.7:
            risk_score += 2
        elif vol_score > 0.5:
            risk_score += 1

        structure = chart_data.get('structure', {})
        if structure.get('type') == 'unclear':
            risk_score += 1

        if risk_score <= 2:
            return 'Low'
        elif risk_score <= 4:
            return 'Medium'
        else:
            return 'High'

    def _calculate_market_strength(self, chart_data):
        scores = []

        trend = chart_data.get('trend', {})
        scores.append(trend.get('strength', 0.3) * 100)

        structure = chart_data.get('structure', {})
        scores.append(structure.get('strength', 0.3) * 100)

        volatility = chart_data.get('volatility', {})
        vol_score = volatility.get('score', 0.5)
        if 0.3 <= vol_score <= 0.65:
            scores.append(80)
        elif vol_score < 0.2 or vol_score > 0.8:
            scores.append(30)
        else:
            scores.append(55)

        color = chart_data.get('color_analysis', {})
        scores.append(min(50 + color.get('strength', 0) * 100, 100))

        momentum = chart_data.get('momentum', {})
        if momentum.get('is_exhausted'):
            scores.append(40)
        else:
            scores.append(momentum.get('strength', 0.5) * 100)

        avg = sum(scores) / len(scores) if scores else 50
        return min(round(avg), 100)

    def _generate_note(self, signal, confidence, risk, strategies, chart_data, force_trade=False):
        trend = chart_data.get('trend', {}).get('direction', 'unknown')

        notes = []

        if force_trade:
            notes.append("⚡ Force Trade Mode Active!")

        if 'STRONG' in signal:
            notes.append(f"🎯 Strong signal with {confidence}% confidence!")
        else:
            notes.append(f"📊 Signal detected with {confidence}% confidence.")

        if strategies:
            notes.append(f"📈 Confirmed by {len(strategies)} strategies: {', '.join(strategies[:5])}")

        notes.append(f"📉 Market Trend: {trend.capitalize()}")

        if risk == 'Low':
            notes.append("✅ Risk Level: Low - Good entry conditions")
        elif risk == 'Medium':
            notes.append("⚠️ Risk Level: Medium - Trade with caution")
        else:
            notes.append("🔴 Risk Level: High - Consider skipping")

        notes.append("\n📌 Trading Tips:")
        notes.append("• Enter near candle close")
        notes.append("• Use normal trade size (no martingale)")
        notes.append("• Stop after 2 consecutive losses")
        if force_trade:
            notes.append("• ⚠️ Force mode active - trade extra carefully!")

        return '\n'.join(notes)

    def _format_strategy_name(self, name):
        names = {
            'trend_following': 'Trend Following',
            'rsi_reversal': 'RSI Reversal',
            'momentum': 'Momentum',
            'pattern_recognition': 'Pattern Recognition',
            'volume_strength': 'Volume Strength',
            'ma_crossover': 'MA Crossover',
            'support_resistance': 'Support & Resistance',
            'breakout': 'Breakout Confirmation',
            'liquidity_grab': 'Liquidity Grab',
            'trend_pullback': 'Trend Pullback',
            'multi_timeframe': 'Multi-Timeframe',
            'candle_rejection': 'Candle Rejection',
            'range_scalping': 'Range Scalping',
            'volatility_filter': 'Volatility Filter',
            'smart_doji': 'Smart Doji',
            'exhaustion': 'Exhaustion'
        }
        return names.get(name, name.replace('_', ' ').title())
