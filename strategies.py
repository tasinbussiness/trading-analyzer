# ===== STRUGGLE AI - STRATEGY ENGINE =====
# Stronger Strategies for Maximum Win Rate
# Force Trade Mode with Better Logic
# strategies.py

import random

class StrategyEngine:
    """
    Maximum Win Rate Strategy Engine
    - Stronger signal generation
    - Better decision logic
    - 90%+ winrate target
    - Force trade with intelligence
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

        # Higher weights for more accurate strategies
        self.weights = {
            'trend_following': 1.8,
            'rsi_reversal': 1.4,
            'momentum': 1.6,
            'pattern_recognition': 1.7,
            'volume_strength': 1.3,
            'ma_crossover': 1.5,
            'support_resistance': 1.8,
            'breakout': 1.6,
            'liquidity_grab': 1.5,
            'trend_pullback': 1.7,
            'multi_timeframe': 1.8,
            'candle_rejection': 1.5,
            'range_scalping': 1.3,
            'volatility_filter': 1.4,
            'smart_doji': 1.2,
            'exhaustion': 1.5
        }

    def analyze(self, chart_data, enabled_strategies=None):
        """Main analysis with intelligent decision making"""
        
        if enabled_strategies is None:
            enabled_strategies = {k: True for k in self.strategies}

        force_trade = enabled_strategies.get('force_trade', False)

        # Run all strategies
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

        # Get overall market direction from data
        market_direction = self._determine_market_direction(chart_data)

        # ===== FILTERS (only if not force_trade) =====
        if not force_trade:
            # Filter 1: Very high volatility
            volatility = chart_data.get('volatility', {})
            if volatility.get('level') == 'high' and volatility.get('score', 0) > 0.90:
                return self._avoid_signal(
                    'অতিরিক্ত ভোলাটাইল মার্কেট! এখন ট্রেড না নেওয়াই ভালো।',
                    chart_data, strategy_names
                )

            # Filter 2: Doji without strong confirmation
            last_candle = chart_data.get('last_candle', {})
            if last_candle.get('is_doji', False):
                confirmed = any(r['confidence'] >= 80 for r in results)
                if not confirmed:
                    return self._avoid_signal(
                        'Doji candle detected! Confirmation candle এর জন্য অপেক্ষা করুন।',
                        chart_data, strategy_names
                    )

            # Filter 3: Extremely unclear structure
            structure = chart_data.get('structure', {})
            if structure.get('type') == 'unclear' and structure.get('strength', 0) < 0.3:
                strong_signals = [r for r in results if r['confidence'] >= 82]
                if len(strong_signals) < 2:
                    return self._avoid_signal(
                        'Market structure unclear! Clear setup এর জন্য অপেক্ষা করুন।',
                        chart_data, strategy_names
                    )

            # Filter 4: Major conflicts
            buy_signals = [r for r in results if r['signal'] == 'BUY']
            sell_signals = [r for r in results if r['signal'] == 'SELL']

            if len(buy_signals) > 0 and len(sell_signals) > 0:
                buy_strength = sum(r['confidence'] * r['weight'] for r in buy_signals)
                sell_strength = sum(r['confidence'] * r['weight'] for r in sell_signals)
                
                # Only avoid if truly conflicting (within 20%)
                if abs(buy_strength - sell_strength) < buy_strength * 0.20:
                    return self._avoid_signal(
                        'Buy এবং Sell signals conflict করছে! Wait করুন।',
                        chart_data, strategy_names
                    )

            # Filter 5: Too many avoids (5+)
            avoid_signals = [r for r in results if r['signal'] == 'AVOID']
            if len(avoid_signals) >= 5:
                return self._avoid_signal(
                    'Multiple strategies avoid suggest করছে!',
                    chart_data, strategy_names
                )

        # If no results, use market direction
        if not results:
            if force_trade:
                return self._smart_force_signal(chart_data, strategy_names, market_direction)
            return self._avoid_signal(
                'No clear signal! Wait for better setup.',
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

        # Determine direction (align with market direction bonus)
        if buy_score > sell_score and buy_count >= 1:
            direction = 'BUY'
            score = buy_score
            count = buy_count
            # Bonus if aligns with market direction
            if market_direction == 'BUY':
                score *= 1.15
        elif sell_score > buy_score and sell_count >= 1:
            direction = 'SELL'
            score = sell_score
            count = sell_count
            if market_direction == 'SELL':
                score *= 1.15
        else:
            if force_trade:
                return self._smart_force_signal(chart_data, strategy_names, market_direction)
            return self._avoid_signal(
                'No dominant signal direction.',
                chart_data, strategy_names
            )

        # Confidence calculation (higher base)
        max_possible = count * 100 * max(self.weights.values())
        raw_confidence = (score / max_possible * 100) if max_possible > 0 else 0

        # Bigger boost for more confirmations
        if count >= 5:
            confidence_boost = 25
        elif count >= 4:
            confidence_boost = 20
        elif count >= 3:
            confidence_boost = 15
        elif count >= 2:
            confidence_boost = 10
        else:
            confidence_boost = 5

        confidence = min(raw_confidence + confidence_boost, 98)

        # Minimum confidence check (lower threshold for stronger signals)
        if not force_trade:
            if confidence < 60:
                return self._avoid_signal(
                    f'Confidence too low ({confidence:.0f}%)! Wait for stronger setup.',
                    chart_data, strategy_names
                )
        else:
            # Force trade - boost confidence
            if confidence < 60:
                confidence = max(confidence + 20, 65)

        # Signal strength (easier to reach STRONG)
        if not force_trade:
            if count >= 3 and confidence >= 82:
                signal = f'STRONG {direction}'
            elif count >= 2 and confidence >= 65:
                signal = direction
            elif count >= 1 and confidence >= 70:
                signal = direction
            else:
                return self._avoid_signal(
                    'Not enough confirmation for safe entry.',
                    chart_data, strategy_names
                )
        else:
            # Force trade always gives signal
            if count >= 3 and confidence >= 78:
                signal = f'STRONG {direction}'
            else:
                signal = direction

        # Risk (recalculated)
        risk = self._calculate_risk(chart_data, confidence, count)

        # Market strength (better calculation)
        market_strength = self._calculate_market_strength(chart_data)

        if not force_trade:
            if market_strength < 40:
                return self._avoid_signal(
                    f'Market strength too low ({market_strength}%)! Better setup wait করুন।',
                    chart_data, strategy_names
                )
        else:
            if market_strength < 45:
                market_strength = 50

        note = self._generate_note(signal, confidence, risk, strategy_names, chart_data, force_trade)

        return {
            'signal': signal,
            'confidence': round(confidence),
            'risk': risk,
            'market_strength': market_strength,
            'strategies': strategy_names,
            'note': note
        }

    def _determine_market_direction(self, chart_data):
        """Determine overall market direction from all data"""
        score = 0
        
        # Trend
        trend = chart_data.get('trend', {})
        if trend.get('direction') == 'uptrend':
            score += trend.get('strength', 0) * 2
        elif trend.get('direction') == 'downtrend':
            score -= trend.get('strength', 0) * 2

        # Structure
        structure = chart_data.get('structure', {})
        if structure.get('type') == 'bullish':
            score += 1.5
        elif structure.get('type') == 'bearish':
            score -= 1.5

        # Last candle
        last_candle = chart_data.get('last_candle', {})
        if last_candle.get('type') == 'bullish':
            score += 1
        elif last_candle.get('type') == 'bearish':
            score -= 1

        # Color analysis
        color = chart_data.get('color_analysis', {})
        if color.get('dominant') == 'bullish':
            score += color.get('strength', 0)
        elif color.get('dominant') == 'bearish':
            score -= color.get('strength', 0)

        # Momentum
        momentum = chart_data.get('momentum', {})
        if momentum.get('direction') == 'bullish' and not momentum.get('is_exhausted'):
            score += momentum.get('strength', 0)
        elif momentum.get('direction') == 'bearish' and not momentum.get('is_exhausted'):
            score -= momentum.get('strength', 0)

        if score > 0.5:
            return 'BUY'
        elif score < -0.5:
            return 'SELL'
        return 'NEUTRAL'

    def _smart_force_signal(self, chart_data, strategy_names, market_direction):
        """Smart force signal - uses market direction"""
        last_candle = chart_data.get('last_candle', {})
        color = chart_data.get('color_analysis', {})
        trend = chart_data.get('trend', {})
        momentum = chart_data.get('momentum', {})

        # Use market direction first
        if market_direction != 'NEUTRAL':
            direction = market_direction
            confidence = 68
        elif last_candle.get('type') == 'bullish':
            direction = 'BUY'
            confidence = 62
        elif last_candle.get('type') == 'bearish':
            direction = 'SELL'
            confidence = 62
        elif color.get('dominant') == 'bullish':
            direction = 'BUY'
            confidence = 60
        elif color.get('dominant') == 'bearish':
            direction = 'SELL'
            confidence = 60
        elif trend.get('direction') == 'uptrend':
            direction = 'BUY'
            confidence = 58
        elif trend.get('direction') == 'downtrend':
            direction = 'SELL'
            confidence = 58
        else:
            direction = 'BUY' if random.random() > 0.5 else 'SELL'
            confidence = 55

        if not strategy_names:
            strategy_names = ['Force Analysis', 'Market Direction']

        return {
            'signal': direction,
            'confidence': confidence,
            'risk': 'Medium',
            'market_strength': 55,
            'strategies': strategy_names,
            'note': f'⚡ Force Trade Mode!\n📊 Signal: {direction}\n⚠️ Trade carefully!\n\n📌 Tips:\n• Small trade size\n• Set stop loss\n• Don\'t over-trade'
        }

    # ============================================
    # ===== STRATEGIES (STRONGER LOGIC) =====
    # ============================================

    def trend_following(self, chart_data):
        trend = chart_data.get('trend', {})
        direction = trend.get('direction', 'sideways')
        strength = trend.get('strength', 0)
        last_candle = chart_data.get('last_candle', {})
        color = chart_data.get('color_analysis', {})

        if direction == 'uptrend' and strength >= 0.4:
            confidence = min(strength * 100 + 15, 95)
            if last_candle.get('type') == 'bullish':
                confidence = min(confidence + 10, 95)
            if color.get('dominant') == 'bullish':
                confidence = min(confidence + 5, 95)
            return {'signal': 'BUY', 'confidence': confidence, 'reason': 'Uptrend'}

        elif direction == 'downtrend' and strength >= 0.4:
            confidence = min(strength * 100 + 15, 95)
            if last_candle.get('type') == 'bearish':
                confidence = min(confidence + 10, 95)
            if color.get('dominant') == 'bearish':
                confidence = min(confidence + 5, 95)
            return {'signal': 'SELL', 'confidence': confidence, 'reason': 'Downtrend'}

        # Weak trend - still give signal
        elif direction == 'uptrend' and last_candle.get('type') == 'bullish':
            return {'signal': 'BUY', 'confidence': 62, 'reason': 'Weak uptrend'}
        elif direction == 'downtrend' and last_candle.get('type') == 'bearish':
            return {'signal': 'SELL', 'confidence': 62, 'reason': 'Weak downtrend'}

        return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

    def rsi_reversal(self, chart_data):
        momentum = chart_data.get('momentum', {})
        last_candle = chart_data.get('last_candle', {})

        continuous = momentum.get('continuous_count', 0)
        is_exhausted = momentum.get('is_exhausted', False)
        last_type = momentum.get('last_type', 'neutral')

        # Strong exhaustion
        if continuous >= 5 and is_exhausted:
            if last_type == 'bullish':
                return {'signal': 'SELL', 'confidence': 82, 'reason': 'Overbought - strong reversal'}
            elif last_type == 'bearish':
                return {'signal': 'BUY', 'confidence': 82, 'reason': 'Oversold - strong reversal'}

        # Medium exhaustion
        if continuous >= 4:
            if last_type == 'bullish' and last_candle.get('has_rejection'):
                return {'signal': 'SELL', 'confidence': 75, 'reason': 'Overbought reversal'}
            elif last_type == 'bearish' and last_candle.get('has_rejection'):
                return {'signal': 'BUY', 'confidence': 75, 'reason': 'Oversold reversal'}

        # Early signs
        if continuous >= 3 and is_exhausted:
            if last_type == 'bullish':
                return {'signal': 'SELL', 'confidence': 65, 'reason': 'Overbought signs'}
            elif last_type == 'bearish':
                return {'signal': 'BUY', 'confidence': 65, 'reason': 'Oversold signs'}

        return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

    def momentum_strategy(self, chart_data):
        momentum = chart_data.get('momentum', {})
        color = chart_data.get('color_analysis', {})
        last_candle = chart_data.get('last_candle', {})

        mom_direction = momentum.get('direction', 'neutral')
        mom_strength = momentum.get('strength', 0.5)
        is_exhausted = momentum.get('is_exhausted', False)

        if is_exhausted and mom_strength > 0.8:
            return {'signal': 'AVOID', 'confidence': 55, 'reason': 'Exhaustion'}

        # Strong momentum
        if mom_strength >= 0.65:
            if mom_direction == 'bullish':
                confidence = min(mom_strength * 100 + 15, 95)
                if last_candle.get('type') == 'bullish':
                    confidence = min(confidence + 8, 95)
                if color.get('dominant') == 'bullish':
                    confidence = min(confidence + 5, 95)
                return {'signal': 'BUY', 'confidence': confidence, 'reason': 'Strong bullish momentum'}
            elif mom_direction == 'bearish':
                confidence = min(mom_strength * 100 + 15, 95)
                if last_candle.get('type') == 'bearish':
                    confidence = min(confidence + 8, 95)
                if color.get('dominant') == 'bearish':
                    confidence = min(confidence + 5, 95)
                return {'signal': 'SELL', 'confidence': confidence, 'reason': 'Strong bearish momentum'}

        # Moderate momentum
        elif mom_strength >= 0.5:
            if mom_direction == 'bullish':
                return {'signal': 'BUY', 'confidence': 70, 'reason': 'Moderate bullish'}
            elif mom_direction == 'bearish':
                return {'signal': 'SELL', 'confidence': 70, 'reason': 'Moderate bearish'}

        return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

    def pattern_recognition(self, chart_data):
        patterns = chart_data.get('patterns', [])
        if not patterns:
            return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

        bullish_patterns = [p for p in patterns if p['type'] == 'bullish']
        bearish_patterns = [p for p in patterns if p['type'] == 'bearish']
        neutral_patterns = [p for p in patterns if p['type'] == 'neutral']

        # Neutral only = avoid
        if neutral_patterns and not bullish_patterns and not bearish_patterns:
            return {'signal': 'AVOID', 'confidence': 55, 'reason': f"Neutral: {neutral_patterns[0]['name']}"}

        # Multiple bullish = strong
        if bullish_patterns:
            best = max(bullish_patterns, key=lambda p: p['reliability'])
            confidence = best['reliability'] * 100 + 5
            if len(bullish_patterns) >= 2:
                confidence = min(confidence + 12, 95)
            if len(bullish_patterns) >= 3:
                confidence = min(confidence + 5, 95)
            return {'signal': 'BUY', 'confidence': min(confidence, 95), 'reason': f"Pattern: {best['name']}"}

        # Multiple bearish = strong
        if bearish_patterns:
            best = max(bearish_patterns, key=lambda p: p['reliability'])
            confidence = best['reliability'] * 100 + 5
            if len(bearish_patterns) >= 2:
                confidence = min(confidence + 12, 95)
            if len(bearish_patterns) >= 3:
                confidence = min(confidence + 5, 95)
            return {'signal': 'SELL', 'confidence': min(confidence, 95), 'reason': f"Pattern: {best['name']}"}

        return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

    def volume_strength(self, chart_data):
        volume = chart_data.get('volume', {})
        trend = chart_data.get('trend', {})
        last_candle = chart_data.get('last_candle', {})
        color = chart_data.get('color_analysis', {})

        if not volume.get('visible', False):
            # Use color as proxy
            if color.get('strength', 0) > 0.25:
                if color.get('dominant') == 'bullish':
                    return {'signal': 'BUY', 'confidence': 65, 'reason': 'Bullish dominance'}
                elif color.get('dominant') == 'bearish':
                    return {'signal': 'SELL', 'confidence': 65, 'reason': 'Bearish dominance'}
            return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

        vol_trend = volume.get('trend', 'stable')
        buy_pressure = volume.get('buy_pressure', False)

        if vol_trend == 'increasing':
            if trend.get('direction') == 'uptrend' and buy_pressure:
                return {'signal': 'BUY', 'confidence': 85, 'reason': 'Rising volume + uptrend'}
            elif trend.get('direction') == 'downtrend' and not buy_pressure:
                return {'signal': 'SELL', 'confidence': 85, 'reason': 'Rising volume + downtrend'}

        if buy_pressure and last_candle.get('type') == 'bullish':
            return {'signal': 'BUY', 'confidence': 72, 'reason': 'Buy volume + bullish'}
        elif not buy_pressure and last_candle.get('type') == 'bearish':
            return {'signal': 'SELL', 'confidence': 72, 'reason': 'Sell volume + bearish'}

        return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

    def ma_crossover(self, chart_data):
        indicators = chart_data.get('indicators', {})
        trend = chart_data.get('trend', {})
        last_candle = chart_data.get('last_candle', {})
        color = chart_data.get('color_analysis', {})

        if not indicators.get('moving_averages', False):
            # Simulated MA from trend
            if trend.get('direction') == 'uptrend' and trend.get('strength', 0) >= 0.5:
                if last_candle.get('type') == 'bullish':
                    return {'signal': 'BUY', 'confidence': 72, 'reason': 'MA bullish alignment'}
            elif trend.get('direction') == 'downtrend' and trend.get('strength', 0) >= 0.5:
                if last_candle.get('type') == 'bearish':
                    return {'signal': 'SELL', 'confidence': 72, 'reason': 'MA bearish alignment'}
            return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

        lines = indicators.get('detected_lines', 0)
        if lines >= 2:
            if trend.get('direction') == 'uptrend':
                return {'signal': 'BUY', 'confidence': 82, 'reason': 'MA crossover bullish'}
            elif trend.get('direction') == 'downtrend':
                return {'signal': 'SELL', 'confidence': 82, 'reason': 'MA crossover bearish'}
        elif lines == 1:
            if color.get('dominant') == 'bullish':
                return {'signal': 'BUY', 'confidence': 68, 'reason': 'Above MA'}
            elif color.get('dominant') == 'bearish':
                return {'signal': 'SELL', 'confidence': 68, 'reason': 'Below MA'}

        return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

    def support_resistance(self, chart_data):
        sr = chart_data.get('support_resistance', {})
        last_candle = chart_data.get('last_candle', {})
        price_action = chart_data.get('price_action', {})

        if price_action.get('fake_breakout', False):
            return {'signal': 'AVOID', 'confidence': 70, 'reason': 'Fake breakout'}

        at_level = sr.get('at_level')

        if at_level == 'support':
            if last_candle.get('type') == 'bullish':
                return {'signal': 'BUY', 'confidence': 88, 'reason': 'Bounce from support'}
            elif last_candle.get('has_rejection') and last_candle.get('rejection_from') == 'bottom':
                return {'signal': 'BUY', 'confidence': 82, 'reason': 'Support rejection'}
            else:
                return {'signal': 'BUY', 'confidence': 70, 'reason': 'At support'}

        elif at_level == 'resistance':
            if last_candle.get('type') == 'bearish':
                return {'signal': 'SELL', 'confidence': 88, 'reason': 'Rejection from resistance'}
            elif last_candle.get('has_rejection') and last_candle.get('rejection_from') == 'top':
                return {'signal': 'SELL', 'confidence': 82, 'reason': 'Resistance rejection'}
            else:
                return {'signal': 'SELL', 'confidence': 70, 'reason': 'At resistance'}

        if sr.get('near_support'):
            if last_candle.get('type') == 'bullish':
                return {'signal': 'BUY', 'confidence': 72, 'reason': 'Near support'}
        if sr.get('near_resistance'):
            if last_candle.get('type') == 'bearish':
                return {'signal': 'SELL', 'confidence': 72, 'reason': 'Near resistance'}

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
            confidence = 88
            if vol_increasing:
                confidence = min(confidence + 7, 95)
            if breakout_dir == 'up':
                return {'signal': 'BUY', 'confidence': confidence, 'reason': 'Strong breakout'}
            elif breakout_dir == 'down':
                return {'signal': 'SELL', 'confidence': confidence, 'reason': 'Strong breakdown'}
        else:
            # Weak breakout still give signal
            if breakout_dir == 'up':
                return {'signal': 'BUY', 'confidence': 65, 'reason': 'Weak breakout'}
            elif breakout_dir == 'down':
                return {'signal': 'SELL', 'confidence': 65, 'reason': 'Weak breakdown'}

        return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

    def liquidity_grab(self, chart_data):
        price_action = chart_data.get('price_action', {})
        last_candle = chart_data.get('last_candle', {})
        sr = chart_data.get('support_resistance', {})

        if price_action.get('liquidity_grab', False):
            if last_candle.get('type') == 'bullish':
                return {'signal': 'BUY', 'confidence': 85, 'reason': 'Liquidity grab bullish'}
            elif last_candle.get('type') == 'bearish':
                return {'signal': 'SELL', 'confidence': 85, 'reason': 'Liquidity grab bearish'}

        if last_candle.get('has_rejection'):
            rejection = last_candle.get('rejection_from')
            if rejection == 'bottom' and last_candle.get('type') == 'bullish':
                if sr.get('near_support'):
                    return {'signal': 'BUY', 'confidence': 78, 'reason': 'Stop hunt below support'}
                return {'signal': 'BUY', 'confidence': 65, 'reason': 'Bottom rejection'}
            elif rejection == 'top' and last_candle.get('type') == 'bearish':
                if sr.get('near_resistance'):
                    return {'signal': 'SELL', 'confidence': 78, 'reason': 'Stop hunt above resistance'}
                return {'signal': 'SELL', 'confidence': 65, 'reason': 'Top rejection'}

        return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

    def trend_pullback(self, chart_data):
        trend = chart_data.get('trend', {})
        price_action = chart_data.get('price_action', {})
        last_candle = chart_data.get('last_candle', {})

        is_pullback = price_action.get('pullback', False)
        trend_dir = trend.get('direction', 'sideways')
        trend_strength = trend.get('strength', 0)

        # Continuation after pullback
        if price_action.get('continuation', False) and trend_strength >= 0.4:
            if trend_dir == 'uptrend' and last_candle.get('type') == 'bullish':
                return {'signal': 'BUY', 'confidence': 78, 'reason': 'Continuation after pullback'}
            elif trend_dir == 'downtrend' and last_candle.get('type') == 'bearish':
                return {'signal': 'SELL', 'confidence': 78, 'reason': 'Continuation after pullback'}

        if not is_pullback:
            return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

        if trend_dir == 'uptrend' and trend_strength >= 0.4:
            if last_candle.get('type') == 'bullish':
                confidence = 82 if last_candle.get('is_strong', False) else 72
                return {'signal': 'BUY', 'confidence': confidence, 'reason': 'Pullback entry uptrend'}

        elif trend_dir == 'downtrend' and trend_strength >= 0.4:
            if last_candle.get('type') == 'bearish':
                confidence = 82 if last_candle.get('is_strong', False) else 72
                return {'signal': 'SELL', 'confidence': confidence, 'reason': 'Pullback entry downtrend'}

        return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

    def multi_timeframe(self, chart_data):
        structure = chart_data.get('structure', {})
        trend = chart_data.get('trend', {})
        last_candle = chart_data.get('last_candle', {})
        color = chart_data.get('color_analysis', {})

        structure_type = structure.get('type', 'unclear')
        trend_dir = trend.get('direction', 'sideways')

        # Perfect alignment
        if (structure_type == 'bullish' and trend_dir == 'uptrend' and last_candle.get('type') == 'bullish'):
            confidence = 90
            if color.get('dominant') == 'bullish':
                confidence = min(confidence + 5, 95)
            return {'signal': 'BUY', 'confidence': confidence, 'reason': 'MTF bullish aligned'}

        elif (structure_type == 'bearish' and trend_dir == 'downtrend' and last_candle.get('type') == 'bearish'):
            confidence = 90
            if color.get('dominant') == 'bearish':
                confidence = min(confidence + 5, 95)
            return {'signal': 'SELL', 'confidence': confidence, 'reason': 'MTF bearish aligned'}

        # Partial alignment
        if structure_type == 'bullish' and last_candle.get('type') == 'bullish':
            return {'signal': 'BUY', 'confidence': 72, 'reason': 'Bullish structure'}
        elif structure_type == 'bearish' and last_candle.get('type') == 'bearish':
            return {'signal': 'SELL', 'confidence': 72, 'reason': 'Bearish structure'}

        # Major conflict
        elif ((structure_type == 'bullish' and trend_dir == 'downtrend') or
              (structure_type == 'bearish' and trend_dir == 'uptrend')):
            return {'signal': 'AVOID', 'confidence': 60, 'reason': 'MTF conflict'}

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
        if wick_ratio < 1.5:
            return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

        if rejection_from == 'top':
            confidence = min(65 + wick_ratio * 5, 88)
            if last_candle.get('type') == 'bearish':
                confidence = min(confidence + 8, 92)
            return {'signal': 'SELL', 'confidence': confidence, 'reason': 'Top rejection'}

        elif rejection_from == 'bottom':
            confidence = min(65 + wick_ratio * 5, 88)
            if last_candle.get('type') == 'bullish':
                confidence = min(confidence + 8, 92)
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
                return {'signal': 'SELL', 'confidence': 78, 'reason': 'Top of range'}
            return {'signal': 'SELL', 'confidence': 65, 'reason': 'At range top'}
        elif range_pos == 'bottom':
            if last_candle.get('type') == 'bullish' or last_candle.get('has_rejection'):
                return {'signal': 'BUY', 'confidence': 78, 'reason': 'Bottom of range'}
            return {'signal': 'BUY', 'confidence': 65, 'reason': 'At range bottom'}
        elif range_pos == 'middle':
            return {'signal': 'AVOID', 'confidence': 55, 'reason': 'Middle of range'}

        return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

    def volatility_filter(self, chart_data):
        volatility = chart_data.get('volatility', {})
        vol_level = volatility.get('level', 'medium')
        vol_score = volatility.get('score', 0.5)
        vol_trend = volatility.get('trend', 'stable')

        if vol_level == 'high' and vol_score > 0.85:
            return {'signal': 'AVOID', 'confidence': 70, 'reason': 'Very high volatility'}

        if vol_level == 'low' and vol_score < 0.15:
            return {'signal': 'AVOID', 'confidence': 55, 'reason': 'Too low volatility'}

        # Optimal
        if 0.25 <= vol_score <= 0.7:
            trend = chart_data.get('trend', {})
            last_candle = chart_data.get('last_candle', {})

            if trend.get('direction') == 'uptrend' and last_candle.get('type') == 'bullish':
                return {'signal': 'BUY', 'confidence': 72, 'reason': 'Optimal volatility bullish'}
            elif trend.get('direction') == 'downtrend' and last_candle.get('type') == 'bearish':
                return {'signal': 'SELL', 'confidence': 72, 'reason': 'Optimal volatility bearish'}

        return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

    def smart_doji(self, chart_data):
        last_candle = chart_data.get('last_candle', {})
        candles = chart_data.get('candles', [])

        if last_candle.get('is_doji', False):
            return {'signal': 'AVOID', 'confidence': 60, 'reason': 'Doji - wait confirmation'}

        if len(candles) >= 2:
            prev = candles[-2]
            if prev.get('body_size', 1) < 0.003:
                if last_candle.get('type') == 'bullish' and last_candle.get('is_strong', False):
                    return {'signal': 'BUY', 'confidence': 82, 'reason': 'Strong bullish after Doji'}
                elif last_candle.get('type') == 'bearish' and last_candle.get('is_strong', False):
                    return {'signal': 'SELL', 'confidence': 82, 'reason': 'Strong bearish after Doji'}
                elif last_candle.get('type') == 'bullish':
                    return {'signal': 'BUY', 'confidence': 68, 'reason': 'Bullish after Doji'}
                elif last_candle.get('type') == 'bearish':
                    return {'signal': 'SELL', 'confidence': 68, 'reason': 'Bearish after Doji'}

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
            has_reversal = any(
                p['name'] in ['Hammer', 'Shooting Star', 'Engulfing', 'Morning Star', 'Evening Star']
                for p in patterns
            )

            if last_type == 'bullish':
                confidence = 75
                if has_reversal:
                    confidence = 88
                if last_candle.get('has_rejection') and last_candle.get('rejection_from') == 'top':
                    confidence = min(confidence + 5, 92)
                return {'signal': 'SELL', 'confidence': confidence, 'reason': 'Bullish exhaustion'}

            elif last_type == 'bearish':
                confidence = 75
                if has_reversal:
                    confidence = 88
                if last_candle.get('has_rejection') and last_candle.get('rejection_from') == 'bottom':
                    confidence = min(confidence + 5, 92)
                return {'signal': 'BUY', 'confidence': confidence, 'reason': 'Bearish exhaustion'}

        elif continuous >= 5:
            if last_type == 'bullish':
                return {'signal': 'AVOID', 'confidence': 62, 'reason': f'{continuous} bullish - exhaustion soon'}
            elif last_type == 'bearish':
                return {'signal': 'AVOID', 'confidence': 62, 'reason': f'{continuous} bearish - exhaustion soon'}

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
            'note': f"⚠️ {reason}\n\n📌 Tips:\n• Wait for clearer conditions\n• Don't force trades\n• Follow money management\n• Enable Force Trade Mode to get signals anyway"
        }

    def _calculate_risk(self, chart_data, confidence, strategy_count):
        volatility = chart_data.get('volatility', {})
        vol_score = volatility.get('score', 0.5)

        risk_score = 0
        
        if confidence >= 85:
            risk_score += 0
        elif confidence >= 75:
            risk_score += 1
        elif confidence >= 65:
            risk_score += 2
        else:
            risk_score += 3

        if strategy_count >= 5:
            risk_score -= 2
        elif strategy_count >= 4:
            risk_score -= 1.5
        elif strategy_count >= 3:
            risk_score -= 1
        elif strategy_count >= 2:
            risk_score -= 0.5

        if vol_score > 0.75:
            risk_score += 2
        elif vol_score > 0.6:
            risk_score += 1

        structure = chart_data.get('structure', {})
        if structure.get('type') == 'unclear':
            risk_score += 1
        elif structure.get('type') in ['bullish', 'bearish']:
            risk_score -= 0.5

        if risk_score <= 1:
            return 'Low'
        elif risk_score <= 3:
            return 'Medium'
        else:
            return 'High'

    def _calculate_market_strength(self, chart_data):
        scores = []

        trend = chart_data.get('trend', {})
        trend_score = trend.get('strength', 0.3) * 100
        if trend.get('direction') != 'sideways':
            trend_score = min(trend_score + 15, 100)
        scores.append(trend_score)

        structure = chart_data.get('structure', {})
        struct_score = structure.get('strength', 0.3) * 100
        if structure.get('type') in ['bullish', 'bearish']:
            struct_score = min(struct_score + 20, 100)
        scores.append(struct_score)

        volatility = chart_data.get('volatility', {})
        vol_score = volatility.get('score', 0.5)
        if 0.3 <= vol_score <= 0.65:
            scores.append(85)
        elif vol_score < 0.2 or vol_score > 0.8:
            scores.append(40)
        else:
            scores.append(65)

        color = chart_data.get('color_analysis', {})
        scores.append(min(60 + color.get('strength', 0) * 100, 100))

        momentum = chart_data.get('momentum', {})
        if momentum.get('is_exhausted'):
            scores.append(50)
        else:
            scores.append(min(momentum.get('strength', 0.5) * 100 + 10, 100))

        avg = sum(scores) / len(scores) if scores else 60
        return min(round(avg), 100)

    def _generate_note(self, signal, confidence, risk, strategies, chart_data, force_trade=False):
        notes = []

        if force_trade:
            notes.append("⚡ Force Trade Mode Active!")

        if 'STRONG' in signal:
            notes.append(f"🎯 Strong signal with {confidence}% confidence!")
        else:
            notes.append(f"📊 Signal detected with {confidence}% confidence.")

        if strategies:
            notes.append(f"📈 Confirmed by {len(strategies)} strategies")

        if risk == 'Low':
            notes.append("✅ Low risk - Good conditions")
        elif risk == 'Medium':
            notes.append("⚠️ Medium risk - Trade carefully")
        else:
            notes.append("🔴 High risk - Consider skipping")

        notes.append("\n📌 Trading Tips:")
        notes.append("• Enter near candle close")
        notes.append("• Use normal trade size (no martingale)")
        notes.append("• Stop after 2 losses")
        notes.append("• Follow money management")

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
