# ===== TRADING STRATEGY ENGINE =====
# All 16 Strategies + Signal Logic
# strategies.py

import random

class StrategyEngine:
    """
    Complete Trading Strategy Engine
    - 6 Base Strategies
    - 10 Advanced Strategies
    - Multi-strategy confirmation
    - 90% winrate target logic
    """

    def __init__(self):
        self.strategies = {
            # Base Strategies
            'trend_following': self.trend_following,
            'rsi_reversal': self.rsi_reversal,
            'momentum': self.momentum_strategy,
            'pattern_recognition': self.pattern_recognition,
            'volume_strength': self.volume_strength,
            'ma_crossover': self.ma_crossover,

            # Advanced Strategies
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

        # Strategy weights for final decision
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

    # ============================================
    # ===== MAIN ANALYSIS =====
    # ============================================

    def analyze(self, chart_data, enabled_strategies=None):
        """
        Run all enabled strategies and generate final signal
        
        Returns:
        {
            'signal': 'STRONG BUY' / 'BUY' / 'SELL' / 'STRONG SELL' / 'AVOID',
            'confidence': 0-100,
            'risk': 'Low' / 'Medium' / 'High',
            'market_strength': 0-100,
            'strategies': [matched strategy names],
            'note': 'explanation text'
        }
        """
        # Default all strategies enabled
        if enabled_strategies is None:
            enabled_strategies = {k: True for k in self.strategies}

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

        # ===== STRICT FILTER CHECKS =====
        
        # Filter 1: Volatility check
        volatility = chart_data.get('volatility', {})
        if volatility.get('level') == 'high' and volatility.get('score', 0) > 0.85:
            return self._avoid_signal(
                'High volatility detected! Market is too unstable for safe trading.',
                chart_data, strategy_names
            )

        # Filter 2: Doji last candle without confirmation
        last_candle = chart_data.get('last_candle', {})
        if last_candle.get('is_doji', False):
            # Check if any strategy confirms direction
            confirmed = any(r['confidence'] >= 75 for r in results)
            if not confirmed:
                return self._avoid_signal(
                    'Doji candle detected without confirmation. Wait for next candle.',
                    chart_data, strategy_names
                )

        # Filter 3: Unclear market structure
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
        avoid_signals = [r for r in results if r['signal'] == 'AVOID']

        if len(buy_signals) > 0 and len(sell_signals) > 0:
            buy_strength = sum(r['confidence'] * r['weight'] for r in buy_signals)
            sell_strength = sum(r['confidence'] * r['weight'] for r in sell_signals)

            # If strengths are close = conflict
            if abs(buy_strength - sell_strength) < buy_strength * 0.3:
                return self._avoid_signal(
                    'Conflicting signals detected. Buy and Sell strategies are conflicting.',
                    chart_data, strategy_names
                )

        # Filter 5: Too many avoid signals
        if len(avoid_signals) >= 3:
            return self._avoid_signal(
                'Multiple strategies suggest avoiding this trade.',
                chart_data, strategy_names
            )

        # ===== GENERATE FINAL SIGNAL =====
        if not results:
            return self._avoid_signal(
                'No clear signal detected. Market conditions are not favorable.',
                chart_data, []
            )

        # Calculate weighted scores
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
            return self._avoid_signal(
                'No dominant signal direction.',
                chart_data, strategy_names
            )

        # ===== CONFIDENCE CALCULATION =====
        max_possible = count * 100 * max(self.weights.values())
        raw_confidence = (score / max_possible * 100) if max_possible > 0 else 0

        # Boost confidence based on strategy count
        if count >= 4:
            confidence_boost = 15
        elif count >= 3:
            confidence_boost = 10
        elif count >= 2:
            confidence_boost = 5
        else:
            confidence_boost = 0

        confidence = min(raw_confidence + confidence_boost, 98)

        # ===== MINIMUM CONFIDENCE CHECK =====
        # For 90% winrate, only show signal when confidence is high
        if confidence < 65:
            return self._avoid_signal(
                f'Signal confidence too low ({confidence:.0f}%). Waiting for stronger setup.',
                chart_data, strategy_names
            )

        # ===== SIGNAL STRENGTH =====
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

        # ===== RISK LEVEL =====
        risk = self._calculate_risk(chart_data, confidence, count)

        # ===== MARKET STRENGTH =====
        market_strength = self._calculate_market_strength(chart_data)

        # Market strength too low
        if market_strength < 40:
            return self._avoid_signal(
                f'Market strength too low ({market_strength}%). Not safe to trade.',
                chart_data, strategy_names
            )

        # ===== GENERATE NOTE =====
        note = self._generate_note(signal, confidence, risk, strategy_names, chart_data)

        return {
            'signal': signal,
            'confidence': round(confidence),
            'risk': risk,
            'market_strength': market_strength,
            'strategies': strategy_names,
            'note': note
        }

    # ============================================
    # ===== BASE STRATEGIES =====
    # ============================================

    def trend_following(self, chart_data):
        """
        Strategy 1: Follow the market trend
        - Uptrend → BUY
        - Downtrend → SELL
        - Sideways → AVOID
        """
        trend = chart_data.get('trend', {})
        direction = trend.get('direction', 'sideways')
        strength = trend.get('strength', 0)
        last_candle = chart_data.get('last_candle', {})

        if direction == 'uptrend' and strength >= 0.5:
            # Confirm with last candle
            if last_candle.get('type') == 'bullish':
                confidence = min(strength * 100 + 15, 95)
            else:
                confidence = min(strength * 100 - 10, 85)

            return {
                'signal': 'BUY',
                'confidence': confidence,
                'reason': 'Strong uptrend detected'
            }

        elif direction == 'downtrend' and strength >= 0.5:
            if last_candle.get('type') == 'bearish':
                confidence = min(strength * 100 + 15, 95)
            else:
                confidence = min(strength * 100 - 10, 85)

            return {
                'signal': 'SELL',
                'confidence': confidence,
                'reason': 'Strong downtrend detected'
            }

        elif direction == 'sideways':
            return {
                'signal': 'AVOID',
                'confidence': 40,
                'reason': 'Sideways market - no clear trend'
            }

        return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

    def rsi_reversal(self, chart_data):
        """
        Strategy 2: RSI Overbought/Oversold Reversal
        Simulated from price action since we can't read exact RSI
        """
        momentum = chart_data.get('momentum', {})
        last_candle = chart_data.get('last_candle', {})
        candles = chart_data.get('candles', [])

        continuous = momentum.get('continuous_count', 0)
        is_exhausted = momentum.get('is_exhausted', False)
        last_type = momentum.get('last_type', 'neutral')

        # Simulate overbought (many consecutive bullish)
        if continuous >= 5 and last_type == 'bullish':
            if is_exhausted or last_candle.get('has_rejection'):
                return {
                    'signal': 'SELL',
                    'confidence': 75,
                    'reason': 'Overbought reversal signal'
                }

        # Simulate oversold (many consecutive bearish)
        elif continuous >= 5 and last_type == 'bearish':
            if is_exhausted or last_candle.get('has_rejection'):
                return {
                    'signal': 'BUY',
                    'confidence': 75,
                    'reason': 'Oversold reversal signal'
                }

        # Moderate reversal
        elif continuous >= 3 and is_exhausted:
            if last_type == 'bullish':
                return {
                    'signal': 'SELL',
                    'confidence': 60,
                    'reason': 'Potential overbought'
                }
            elif last_type == 'bearish':
                return {
                    'signal': 'BUY',
                    'confidence': 60,
                    'reason': 'Potential oversold'
                }

        return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

    def momentum_strategy(self, chart_data):
        """
        Strategy 3: Market Momentum Analysis
        """
        momentum = chart_data.get('momentum', {})
        color_analysis = chart_data.get('color_analysis', {})
        last_candle = chart_data.get('last_candle', {})

        mom_direction = momentum.get('direction', 'neutral')
        mom_strength = momentum.get('strength', 0.5)
        is_exhausted = momentum.get('is_exhausted', False)

        # Skip if exhausted
        if is_exhausted:
            return {
                'signal': 'AVOID',
                'confidence': 55,
                'reason': 'Momentum exhaustion detected'
            }

        # Strong momentum
        if mom_strength >= 0.7 and not is_exhausted:
            if mom_direction == 'bullish' and last_candle.get('type') == 'bullish':
                # Confirm with color analysis
                if color_analysis.get('dominant') == 'bullish':
                    return {
                        'signal': 'BUY',
                        'confidence': min(mom_strength * 100 + 10, 92),
                        'reason': 'Strong bullish momentum'
                    }
                return {
                    'signal': 'BUY',
                    'confidence': min(mom_strength * 100, 85),
                    'reason': 'Bullish momentum'
                }

            elif mom_direction == 'bearish' and last_candle.get('type') == 'bearish':
                if color_analysis.get('dominant') == 'bearish':
                    return {
                        'signal': 'SELL',
                        'confidence': min(mom_strength * 100 + 10, 92),
                        'reason': 'Strong bearish momentum'
                    }
                return {
                    'signal': 'SELL',
                    'confidence': min(mom_strength * 100, 85),
                    'reason': 'Bearish momentum'
                }

        # Moderate momentum
        elif mom_strength >= 0.55:
            if mom_direction == 'bullish':
                return {
                    'signal': 'BUY',
                    'confidence': min(mom_strength * 100 - 5, 75),
                    'reason': 'Moderate bullish momentum'
                }
            elif mom_direction == 'bearish':
                return {
                    'signal': 'SELL',
                    'confidence': min(mom_strength * 100 - 5, 75),
                    'reason': 'Moderate bearish momentum'
                }

        return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

    def pattern_recognition(self, chart_data):
        """
        Strategy 4: Candlestick Pattern Detection
        """
        patterns = chart_data.get('patterns', [])

        if not patterns:
            return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

        # Find strongest pattern
        bullish_patterns = [p for p in patterns if p['type'] == 'bullish']
        bearish_patterns = [p for p in patterns if p['type'] == 'bearish']
        neutral_patterns = [p for p in patterns if p['type'] == 'neutral']

        # Neutral patterns (Doji etc) = avoid
        if neutral_patterns and not bullish_patterns and not bearish_patterns:
            return {
                'signal': 'AVOID',
                'confidence': 50,
                'reason': f"Neutral pattern: {neutral_patterns[0]['name']}"
            }

        # Strong bullish pattern
        if bullish_patterns:
            best = max(bullish_patterns, key=lambda p: p['reliability'])
            confidence = best['reliability'] * 100

            # Boost for multiple patterns
            if len(bullish_patterns) >= 2:
                confidence = min(confidence + 10, 95)

            return {
                'signal': 'BUY',
                'confidence': confidence,
                'reason': f"Pattern: {best['name']}"
            }

        # Strong bearish pattern
        if bearish_patterns:
            best = max(bearish_patterns, key=lambda p: p['reliability'])
            confidence = best['reliability'] * 100

            if len(bearish_patterns) >= 2:
                confidence = min(confidence + 10, 95)

            return {
                'signal': 'SELL',
                'confidence': confidence,
                'reason': f"Pattern: {best['name']}"
            }

        return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

    def volume_strength(self, chart_data):
        """
        Strategy 5: Volume Analysis for Confirmation
        """
        volume = chart_data.get('volume', {})
        trend = chart_data.get('trend', {})
        last_candle = chart_data.get('last_candle', {})

        if not volume.get('visible', False):
            # No volume data - use color analysis as proxy
            color = chart_data.get('color_analysis', {})
            if color.get('strength', 0) > 0.3:
                if color.get('dominant') == 'bullish':
                    return {
                        'signal': 'BUY',
                        'confidence': 60,
                        'reason': 'Bullish color dominance'
                    }
                elif color.get('dominant') == 'bearish':
                    return {
                        'signal': 'SELL',
                        'confidence': 60,
                        'reason': 'Bearish color dominance'
                    }
            return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

        vol_trend = volume.get('trend', 'stable')
        buy_pressure = volume.get('buy_pressure', False)

        # Increasing volume confirms trend
        if vol_trend == 'increasing':
            if trend.get('direction') == 'uptrend' and buy_pressure:
                return {
                    'signal': 'BUY',
                    'confidence': 78,
                    'reason': 'Increasing volume confirms uptrend'
                }
            elif trend.get('direction') == 'downtrend' and not buy_pressure:
                return {
                    'signal': 'SELL',
                    'confidence': 78,
                    'reason': 'Increasing volume confirms downtrend'
                }

        # Decreasing volume - trend weakening
        elif vol_trend == 'decreasing':
            if trend.get('direction') == 'uptrend':
                return {
                    'signal': 'AVOID',
                    'confidence': 55,
                    'reason': 'Decreasing volume - uptrend weakening'
                }
            elif trend.get('direction') == 'downtrend':
                return {
                    'signal': 'AVOID',
                    'confidence': 55,
                    'reason': 'Decreasing volume - downtrend weakening'
                }

        # Volume with candle confirmation
        if buy_pressure and last_candle.get('type') == 'bullish':
            return {
                'signal': 'BUY',
                'confidence': 65,
                'reason': 'Buy volume with bullish candle'
            }
        elif not buy_pressure and last_candle.get('type') == 'bearish':
            return {
                'signal': 'SELL',
                'confidence': 65,
                'reason': 'Sell volume with bearish candle'
            }

        return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

    def ma_crossover(self, chart_data):
        """
        Strategy 6: Moving Average Crossover
        Simulated from detected indicators and trend
        """
        indicators = chart_data.get('indicators', {})
        trend = chart_data.get('trend', {})
        last_candle = chart_data.get('last_candle', {})
        color_analysis = chart_data.get('color_analysis', {})

        if not indicators.get('moving_averages', False):
            # Simulate MA from trend data
            if trend.get('direction') == 'uptrend' and trend.get('strength', 0) >= 0.6:
                if last_candle.get('type') == 'bullish':
                    return {
                        'signal': 'BUY',
                        'confidence': 68,
                        'reason': 'Simulated MA bullish alignment'
                    }
            elif trend.get('direction') == 'downtrend' and trend.get('strength', 0) >= 0.6:
                if last_candle.get('type') == 'bearish':
                    return {
                        'signal': 'SELL',
                        'confidence': 68,
                        'reason': 'Simulated MA bearish alignment'
                    }

            return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

        # MA lines detected
        lines = indicators.get('detected_lines', 0)

        if lines >= 2:
            # Multiple MAs - check trend alignment
            if trend.get('direction') == 'uptrend':
                return {
                    'signal': 'BUY',
                    'confidence': 75,
                    'reason': 'MA crossover bullish with multiple lines'
                }
            elif trend.get('direction') == 'downtrend':
                return {
                    'signal': 'SELL',
                    'confidence': 75,
                    'reason': 'MA crossover bearish with multiple lines'
                }

        elif lines == 1:
            if color_analysis.get('dominant') == 'bullish':
                return {
                    'signal': 'BUY',
                    'confidence': 62,
                    'reason': 'Price above MA line'
                }
            elif color_analysis.get('dominant') == 'bearish':
                return {
                    'signal': 'SELL',
                    'confidence': 62,
                    'reason': 'Price below MA line'
                }

        return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

    # ============================================
    # ===== ADVANCED STRATEGIES =====
    # ============================================

    def support_resistance(self, chart_data):
        """
        Strategy 7: Support & Resistance Bounce
        - At resistance → SELL
        - At support → BUY
        - Fake breakout → AVOID
        """
        sr = chart_data.get('support_resistance', {})
        last_candle = chart_data.get('last_candle', {})
        price_action = chart_data.get('price_action', {})

        # Fake breakout check
        if price_action.get('fake_breakout', False):
            return {
                'signal': 'AVOID',
                'confidence': 70,
                'reason': 'Fake breakout at S/R level'
            }

        at_level = sr.get('at_level')

        if at_level == 'support':
            if last_candle.get('type') == 'bullish':
                return {
                    'signal': 'BUY',
                    'confidence': 80,
                    'reason': 'Bullish bounce from support'
                }
            elif last_candle.get('has_rejection') and last_candle.get('rejection_from') == 'bottom':
                return {
                    'signal': 'BUY',
                    'confidence': 75,
                    'reason': 'Rejection from support level'
                }

        elif at_level == 'resistance':
            if last_candle.get('type') == 'bearish':
                return {
                    'signal': 'SELL',
                    'confidence': 80,
                    'reason': 'Bearish rejection from resistance'
                }
            elif last_candle.get('has_rejection') and last_candle.get('rejection_from') == 'top':
                return {
                    'signal': 'SELL',
                    'confidence': 75,
                    'reason': 'Rejection from resistance level'
                }

        # Near S/R but not confirmed
        if sr.get('near_support') and last_candle.get('type') != 'bullish':
            return {
                'signal': 'AVOID',
                'confidence': 55,
                'reason': 'Near support but no bullish confirmation'
            }
        if sr.get('near_resistance') and last_candle.get('type') != 'bearish':
            return {
                'signal': 'AVOID',
                'confidence': 55,
                'reason': 'Near resistance but no bearish confirmation'
            }

        return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

    def breakout_confirmation(self, chart_data):
        """
        Strategy 8: Breakout Confirmation
        - Consolidation + Strong breakout = trade
        - Weak breakout = avoid
        """
        consolidation = chart_data.get('consolidation', {})
        last_candle = chart_data.get('last_candle', {})
        volume = chart_data.get('volume', {})

        is_breakout = consolidation.get('is_breakout', False)
        breakout_dir = consolidation.get('breakout_direction')

        if not is_breakout:
            if consolidation.get('is_consolidating'):
                return {
                    'signal': 'AVOID',
                    'confidence': 60,
                    'reason': 'Market consolidating - wait for breakout'
                }
            return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

        # Breakout detected - check strength
        is_strong = last_candle.get('is_strong', False)
        is_marubozu = last_candle.get('is_marubozu', False)
        vol_increasing = volume.get('trend') == 'increasing'

        # Strong breakout
        if is_strong or is_marubozu:
            confidence = 82

            if vol_increasing:
                confidence = min(confidence + 8, 93)

            if breakout_dir == 'up':
                return {
                    'signal': 'BUY',
                    'confidence': confidence,
                    'reason': 'Strong bullish breakout confirmed'
                }
            elif breakout_dir == 'down':
                return {
                    'signal': 'SELL',
                    'confidence': confidence,
                    'reason': 'Strong bearish breakout confirmed'
                }

        # Weak breakout
        else:
            return {
                'signal': 'AVOID',
                'confidence': 55,
                'reason': 'Weak breakout - not confirmed'
            }

        return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

    def liquidity_grab(self, chart_data):
        """
        Strategy 9: Liquidity Grab Detection
        - Equal highs/lows sweep
        - Stop hunt identification
        - Reverse signal after grab
        """
        price_action = chart_data.get('price_action', {})
        last_candle = chart_data.get('last_candle', {})
        sr = chart_data.get('support_resistance', {})

        if price_action.get('liquidity_grab', False):
            if last_candle.get('type') == 'bullish':
                return {
                    'signal': 'BUY',
                    'confidence': 78,
                    'reason': 'Liquidity grab with bullish reversal'
                }
            elif last_candle.get('type') == 'bearish':
                return {
                    'signal': 'SELL',
                    'confidence': 78,
                    'reason': 'Liquidity grab with bearish reversal'
                }

        # Check for stop hunt pattern
        if last_candle.get('has_rejection'):
            rejection = last_candle.get('rejection_from')

            if rejection == 'bottom' and last_candle.get('type') == 'bullish':
                if sr.get('near_support'):
                    return {
                        'signal': 'BUY',
                        'confidence': 73,
                        'reason': 'Stop hunt below support with reversal'
                    }

            elif rejection == 'top' and last_candle.get('type') == 'bearish':
                if sr.get('near_resistance'):
                    return {
                        'signal': 'SELL',
                        'confidence': 73,
                        'reason': 'Stop hunt above resistance with reversal'
                    }

        return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

    def trend_pullback(self, chart_data):
        """
        Strategy 10: Trend + Pullback Entry
        - Detect trend
        - Wait for pullback
        - Enter on pullback end
        """
        trend = chart_data.get('trend', {})
        price_action = chart_data.get('price_action', {})
        last_candle = chart_data.get('last_candle', {})
        momentum = chart_data.get('momentum', {})

        is_pullback = price_action.get('pullback', False)
        trend_dir = trend.get('direction', 'sideways')
        trend_strength = trend.get('strength', 0)

        if not is_pullback or trend_dir == 'sideways':
            # Check for continuation after pullback
            if price_action.get('continuation', False) and trend_strength >= 0.5:
                if trend_dir == 'uptrend' and last_candle.get('type') == 'bullish':
                    return {
                        'signal': 'BUY',
                        'confidence': 72,
                        'reason': 'Trend continuation after pullback'
                    }
                elif trend_dir == 'downtrend' and last_candle.get('type') == 'bearish':
                    return {
                        'signal': 'SELL',
                        'confidence': 72,
                        'reason': 'Trend continuation after pullback'
                    }

            return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

        # Pullback in uptrend
        if trend_dir == 'uptrend' and trend_strength >= 0.5:
            # Wait for pullback to show reversal back to trend
            if last_candle.get('type') == 'bullish' and last_candle.get('is_strong', False):
                return {
                    'signal': 'BUY',
                    'confidence': 80,
                    'reason': 'Strong pullback entry in uptrend'
                }
            elif last_candle.get('type') == 'bullish':
                return {
                    'signal': 'BUY',
                    'confidence': 70,
                    'reason': 'Pullback entry in uptrend'
                }

        # Pullback in downtrend
        elif trend_dir == 'downtrend' and trend_strength >= 0.5:
            if last_candle.get('type') == 'bearish' and last_candle.get('is_strong', False):
                return {
                    'signal': 'SELL',
                    'confidence': 80,
                    'reason': 'Strong pullback entry in downtrend'
                }
            elif last_candle.get('type') == 'bearish':
                return {
                    'signal': 'SELL',
                    'confidence': 70,
                    'reason': 'Pullback entry in downtrend'
                }

        return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

    def multi_timeframe(self, chart_data):
        """
        Strategy 11: Multi-Timeframe Confirmation
        Simulated by using overall structure + recent action
        """
        structure = chart_data.get('structure', {})
        trend = chart_data.get('trend', {})
        last_candle = chart_data.get('last_candle', {})
        color_analysis = chart_data.get('color_analysis', {})

        structure_type = structure.get('type', 'unclear')
        trend_dir = trend.get('direction', 'sideways')

        # Higher timeframe = structure, Lower timeframe = recent candles
        # Both must agree

        # Bullish alignment
        if (structure_type == 'bullish' and
            trend_dir == 'uptrend' and
            last_candle.get('type') == 'bullish'):

            confidence = 85
            if color_analysis.get('dominant') == 'bullish':
                confidence = min(confidence + 5, 93)

            return {
                'signal': 'BUY',
                'confidence': confidence,
                'reason': 'Multi-timeframe bullish alignment'
            }

        # Bearish alignment
        elif (structure_type == 'bearish' and
              trend_dir == 'downtrend' and
              last_candle.get('type') == 'bearish'):

            confidence = 85
            if color_analysis.get('dominant') == 'bearish':
                confidence = min(confidence + 5, 93)

            return {
                'signal': 'SELL',
                'confidence': confidence,
                'reason': 'Multi-timeframe bearish alignment'
            }

        # Conflict between timeframes
        elif ((structure_type == 'bullish' and trend_dir == 'downtrend') or
              (structure_type == 'bearish' and trend_dir == 'uptrend')):
            return {
                'signal': 'AVOID',
                'confidence': 65,
                'reason': 'Multi-timeframe conflict detected'
            }

        return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

    def candle_rejection(self, chart_data):
        """
        Strategy 12: Candle Rejection Analysis
        - Long wick = rejection
        - Direction of rejection = signal
        """
        last_candle = chart_data.get('last_candle', {})

        if not last_candle.get('has_rejection', False):
            return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

        rejection_from = last_candle.get('rejection_from')
        upper_wick = last_candle.get('upper_wick', 0)
        lower_wick = last_candle.get('lower_wick', 0)
        body_size = last_candle.get('body_size', 0)

        # Strong rejection
        wick_ratio = max(upper_wick, lower_wick) / body_size if body_size > 0 else 0

        if wick_ratio < 2:
            return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

        # Rejection from top = bearish
        if rejection_from == 'top':
            confidence = min(60 + wick_ratio * 5, 82)
            if last_candle.get('type') == 'bearish':
                confidence = min(confidence + 8, 88)

            return {
                'signal': 'SELL',
                'confidence': confidence,
                'reason': 'Strong rejection from top'
            }

        # Rejection from bottom = bullish
        elif rejection_from == 'bottom':
            confidence = min(60 + wick_ratio * 5, 82)
            if last_candle.get('type') == 'bullish':
                confidence = min(confidence + 8, 88)

            return {
                'signal': 'BUY',
                'confidence': confidence,
                'reason': 'Strong rejection from bottom'
            }

        return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

    def range_scalping(self, chart_data):
        """
        Strategy 13: Range/Sideways Market Scalping
        - Top of range → SELL
        - Bottom of range → BUY
        - Middle → AVOID
        """
        consolidation = chart_data.get('consolidation', {})
        last_candle = chart_data.get('last_candle', {})
        trend = chart_data.get('trend', {})

        # Only in sideways market
        if trend.get('direction') != 'sideways' and not consolidation.get('is_consolidating'):
            return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

        range_pos = consolidation.get('range_position', 'middle')

        if range_pos == 'top':
            if last_candle.get('type') == 'bearish' or last_candle.get('has_rejection'):
                return {
                    'signal': 'SELL',
                    'confidence': 72,
                    'reason': 'Sell at top of range'
                }

        elif range_pos == 'bottom':
            if last_candle.get('type') == 'bullish' or last_candle.get('has_rejection'):
                return {
                    'signal': 'BUY',
                    'confidence': 72,
                    'reason': 'Buy at bottom of range'
                }

        elif range_pos == 'middle':
            return {
                'signal': 'AVOID',
                'confidence': 60,
                'reason': 'Middle of range - no edge'
            }

        return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

    def volatility_filter(self, chart_data):
        """
        Strategy 14: Volatility Filter
        - High volatility → AVOID
        - Low volatility → AVOID
        - Optimal → Allow trade
        """
        volatility = chart_data.get('volatility', {})
        vol_level = volatility.get('level', 'medium')
        vol_score = volatility.get('score', 0.5)
        vol_trend = volatility.get('trend', 'stable')

        # High volatility = dangerous
        if vol_level == 'high':
            return {
                'signal': 'AVOID',
                'confidence': 75,
                'reason': 'High volatility - too risky'
            }

        # Very low volatility = no movement
        if vol_level == 'low' and vol_score < 0.2:
            return {
                'signal': 'AVOID',
                'confidence': 60,
                'reason': 'Very low volatility - no movement'
            }

        # Increasing volatility = caution
        if vol_trend == 'increasing' and vol_score > 0.6:
            return {
                'signal': 'AVOID',
                'confidence': 55,
                'reason': 'Volatility increasing rapidly'
            }

        # Optimal volatility
        if vol_level == 'medium' and 0.3 <= vol_score <= 0.65:
            # Get trend direction for signal
            trend = chart_data.get('trend', {})
            last_candle = chart_data.get('last_candle', {})

            if trend.get('direction') == 'uptrend' and last_candle.get('type') == 'bullish':
                return {
                    'signal': 'BUY',
                    'confidence': 65,
                    'reason': 'Optimal volatility for bullish trade'
                }
            elif trend.get('direction') == 'downtrend' and last_candle.get('type') == 'bearish':
                return {
                    'signal': 'SELL',
                    'confidence': 65,
                    'reason': 'Optimal volatility for bearish trade'
                }

        return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

    def smart_doji(self, chart_data):
        """
        Strategy 15: Smart Doji Detection
        - Doji alone = AVOID
        - Doji + confirmation candle = trade
        """
        last_candle = chart_data.get('last_candle', {})
        candles = chart_data.get('candles', [])
        trend = chart_data.get('trend', {})

        # Check if last candle is doji
        if last_candle.get('is_doji', False):
            return {
                'signal': 'AVOID',
                'confidence': 65,
                'reason': 'Doji detected - wait for confirmation'
            }

        # Check if previous candle was doji (current is confirmation)
        if len(candles) >= 2:
            prev = candles[-2]
            if prev.get('body_size', 1) < 0.003:  # Previous was doji
                # Current candle is confirmation
                if last_candle.get('type') == 'bullish' and last_candle.get('is_strong', False):
                    return {
                        'signal': 'BUY',
                        'confidence': 75,
                        'reason': 'Bullish confirmation after Doji'
                    }
                elif last_candle.get('type') == 'bearish' and last_candle.get('is_strong', False):
                    return {
                        'signal': 'SELL',
                        'confidence': 75,
                        'reason': 'Bearish confirmation after Doji'
                    }
                else:
                    return {
                        'signal': 'AVOID',
                        'confidence': 55,
                        'reason': 'Weak confirmation after Doji'
                    }

        return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

    def exhaustion_strategy(self, chart_data):
        """
        Strategy 16: Market Exhaustion Reversal
        - Continuous move + weak momentum = reversal
        """
        momentum = chart_data.get('momentum', {})
        last_candle = chart_data.get('last_candle', {})
        patterns = chart_data.get('patterns', [])

        continuous = momentum.get('continuous_count', 0)
        is_exhausted = momentum.get('is_exhausted', False)
        last_type = momentum.get('last_type', 'neutral')

        if not is_exhausted and continuous < 4:
            return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

        # Exhaustion confirmed
        if is_exhausted:
            # Look for reversal confirmation
            has_reversal_pattern = any(
                p['name'] in ['Hammer', 'Shooting Star', 'Engulfing', 'Morning Star', 'Evening Star']
                for p in patterns
            )

            if last_type == 'bullish':
                # Exhausted bullish = potential sell
                confidence = 70
                if has_reversal_pattern:
                    confidence = 82
                if last_candle.get('has_rejection') and last_candle.get('rejection_from') == 'top':
                    confidence = min(confidence + 5, 88)

                return {
                    'signal': 'SELL',
                    'confidence': confidence,
                    'reason': 'Bullish exhaustion - reversal expected'
                }

            elif last_type == 'bearish':
                confidence = 70
                if has_reversal_pattern:
                    confidence = 82
                if last_candle.get('has_rejection') and last_candle.get('rejection_from') == 'bottom':
                    confidence = min(confidence + 5, 88)

                return {
                    'signal': 'BUY',
                    'confidence': confidence,
                    'reason': 'Bearish exhaustion - reversal expected'
                }

        # Long continuous move without exhaustion yet
        elif continuous >= 5:
            if last_type == 'bullish':
                return {
                    'signal': 'AVOID',
                    'confidence': 60,
                    'reason': f'{continuous} consecutive bullish candles - possible exhaustion'
                }
            elif last_type == 'bearish':
                return {
                    'signal': 'AVOID',
                    'confidence': 60,
                    'reason': f'{continuous} consecutive bearish candles - possible exhaustion'
                }

        return {'signal': 'NEUTRAL', 'confidence': 0, 'reason': ''}

    # ============================================
    # ===== HELPER FUNCTIONS =====
    # ============================================

    def _avoid_signal(self, reason, chart_data, strategies):
        """Generate AVOID signal"""
        market_strength = self._calculate_market_strength(chart_data)

        return {
            'signal': 'AVOID',
            'confidence': 0,
            'risk': 'High',
            'market_strength': market_strength,
            'strategies': strategies,
            'note': f"⚠️ {reason}\n\n📌 Tips:\n• Wait for clearer market conditions\n• Don't force trades\n• Take a break if needed\n• Follow money management rules"
        }

    def _calculate_risk(self, chart_data, confidence, strategy_count):
        """Calculate risk level"""
        volatility = chart_data.get('volatility', {})
        vol_score = volatility.get('score', 0.5)

        risk_score = 0

        # Higher confidence = lower risk
        if confidence >= 85:
            risk_score += 1
        elif confidence >= 70:
            risk_score += 2
        else:
            risk_score += 3

        # More strategies = lower risk
        if strategy_count >= 4:
            risk_score -= 1
        elif strategy_count >= 3:
            risk_score -= 0.5

        # High volatility = higher risk
        if vol_score > 0.7:
            risk_score += 2
        elif vol_score > 0.5:
            risk_score += 1

        # Unclear structure = higher risk
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
        """Calculate overall market strength (0-100)"""
        scores = []

        # Trend strength
        trend = chart_data.get('trend', {})
        trend_str = trend.get('strength', 0.3)
        scores.append(trend_str * 100)

        # Structure clarity
        structure = chart_data.get('structure', {})
        struct_str = structure.get('strength', 0.3)
        scores.append(struct_str * 100)

        # Volatility (medium is best)
        volatility = chart_data.get('volatility', {})
        vol_score = volatility.get('score', 0.5)
        if 0.3 <= vol_score <= 0.65:
            scores.append(80)
        elif vol_score < 0.2 or vol_score > 0.8:
            scores.append(30)
        else:
            scores.append(55)

        # Color dominance
        color = chart_data.get('color_analysis', {})
        color_str = color.get('strength', 0)
        scores.append(min(50 + color_str * 100, 100))

        # Momentum
        momentum = chart_data.get('momentum', {})
        mom_str = momentum.get('strength', 0.5)
        if momentum.get('is_exhausted'):
            scores.append(40)
        else:
            scores.append(mom_str * 100)

        avg = sum(scores) / len(scores) if scores else 50
        return min(round(avg), 100)

    def _generate_note(self, signal, confidence, risk, strategies, chart_data):
        """Generate human-readable analysis note"""
        trend = chart_data.get('trend', {}).get('direction', 'unknown')
        volatility = chart_data.get('volatility', {}).get('level', 'unknown')
        last_type = chart_data.get('last_candle', {}).get('type', 'unknown')

        notes = []

        # Signal info
        if 'STRONG' in signal:
            notes.append(f"🎯 Strong signal detected with {confidence}% confidence!")
        else:
            notes.append(f"📊 Signal detected with {confidence}% confidence.")

        # Strategies
        if strategies:
            notes.append(f"📈 Confirmed by {len(strategies)} strategies: {', '.join(strategies[:5])}")

        # Trend
        notes.append(f"📉 Market Trend: {trend.capitalize()}")

        # Risk
        if risk == 'Low':
            notes.append("✅ Risk Level: Low - Good entry conditions")
        elif risk == 'Medium':
            notes.append("⚠️ Risk Level: Medium - Trade with caution")
        else:
            notes.append("🔴 Risk Level: High - Consider skipping")

        # Trading tips
        notes.append("\n📌 Trading Tips:")
        notes.append("• Enter near candle close for safe entry")
        notes.append("• Use normal trade size (no martingale)")
        notes.append("• Stop after 2 consecutive losses")
        notes.append("• Take a break if confused")

        return '\n'.join(notes)

    def _format_strategy_name(self, name):
        """Format strategy name for display"""
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