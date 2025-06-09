"""
Flask Web Server for NBA Sports Betting Chatbot Frontend
Serves the HTML interface and provides API endpoints for the chatbot
"""

import os
import asyncio
import json
import time
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from nba_chatbot import NBAChatbot
import threading
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__, static_folder='static', template_folder='static')
CORS(app)

# Initialize the chatbot
chatbot = NBAChatbot()
executor = ThreadPoolExecutor(max_workers=4)

@app.route('/')
def index():
    """Serve the main chatbot interface"""
    return send_from_directory('static', 'index.html')

@app.route('/api/chat', methods=['POST'])
def chat_api():
    """API endpoint for chatbot interactions"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        session_state = data.get('session_state', {})
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Process the message with session state
        def process_message():
            return process_user_message_with_state(user_message, session_state)
          # Run in thread pool to avoid blocking
        future = executor.submit(process_message)
        response = future.result(timeout=180)  # 3 minute timeout for NBA data fetching
        
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Error in chat API: {e}")
        return jsonify({
            'type': 'error',
            'message': f'Sorry, I encountered an error: {str(e)}. Please try again.',
            'session_state': {}
        }), 500

def process_user_message_with_state(message, session_state):
    """Process user message with session state management to replicate original flow"""
    try:
        message_lower = message.lower().strip()
        current_step = session_state.get('step', 'initial')
        
        # Step 1: Initial - Show upcoming games and options
        if current_step == 'initial':
            return handle_initial_step()
            
        # Step 2: User chooses between upcoming games (1) or manual entry (2)
        elif current_step == 'choose_option':
            return handle_option_choice(message, session_state)
            
        # Step 3a: If chose upcoming games, select game by number
        elif current_step == 'select_game':
            return handle_game_selection(message, session_state)
            
        # Step 3b: If chose upcoming games, select which team to analyze
        elif current_step == 'choose_team_from_game':
            return handle_team_choice_from_game(message, session_state)
            
        # Step 4a: If chose manual, enter first team
        elif current_step == 'enter_team1':
            return handle_team1_entry(message, session_state)
            
        # Step 4b: Enter second team
        elif current_step == 'enter_team2':
            return handle_team2_entry(message, session_state)
            
        # Step 4c: Choose which team plays at home
        elif current_step == 'choose_home_team':
            return handle_home_team_choice(message, session_state)
            
        # Step 4d: Choose which team to analyze for betting
        elif current_step == 'choose_team_to_analyze':
            return handle_analysis_team_choice(message, session_state)
            
        # Default case - restart flow
        else:
            return handle_initial_step()
            
    except Exception as e:
        print(f"❌ Error processing message with state: {e}")
        return {
            'type': 'message',
            'message': 'Sorry, I encountered an error processing your request. Please try again.',
            'session_state': {'step': 'initial'}
        }

def handle_initial_step():
    """Step 1: Show upcoming games and initial options"""
    try:
        games = chatbot.data_fetcher.get_upcoming_games()
        
        if not games:
            # No games available, go directly to manual entry
            return {
                'type': 'message',
                'message': '''🏀 **NBA Betting Expert - Welcome!**

❌ No upcoming games found or API error. You can still analyze any two teams manually.

📝 **Enter two NBA teams to analyze:**

💡 **Tip:** You can enter team names like 'Lakers', 'Warriors', 'Celtics', etc.

Please enter the first team:''',
                'session_state': {'step': 'enter_team1'}
            }
        
        # Format games list exactly like original chatbot
        games_text = f'''🏀 **NBA Betting Expert - Welcome!**

🔄 **Fetching upcoming NBA games...**

📅 **Upcoming NBA Games ({len(games)} found):**
{'─' * 60}

'''
        
        for i, game in enumerate(games, 1):
            date_str = game.date if game.date else "TBD"
            time_str = game.time if game.time else "TBD"
            venue_str = f" at {game.venue}" if game.venue else ""
            
            games_text += f"**{i:2d}.** {game.away_team} @ {game.home_team}\n"
            games_text += f"    📅 {date_str} {time_str}{venue_str}\n\n"
        
        games_text += '''**Choose an option:**
**1.** Select from upcoming games
**2.** Enter two teams manually

Enter your choice (1 or 2):'''
        
        return {
            'type': 'message',
            'message': games_text,
            'session_state': {
                'step': 'choose_option',
                'games': [{'away_team': g.away_team, 'home_team': g.home_team, 'date': g.date, 'time': g.time, 'venue': g.venue} for g in games]
            }
        }
        
    except Exception as e:
        return {
            'type': 'message',
            'message': '❌ Error fetching games. Please try again.',
            'session_state': {'step': 'initial'}
        }

def handle_option_choice(message, session_state):
    """Step 2: Handle choice between upcoming games or manual entry"""
    if message == "1":
        games = session_state.get('games', [])
        if not games:
            return {
                'type': 'message',
                'message': '❌ No games available. Please try again.',
                'session_state': {'step': 'initial'}
            }
        
        return {
            'type': 'message',
            'message': f'''✅ **You chose: Select from upcoming games**

Select game number (1-{len(games)}):''',
            'session_state': {
                'step': 'select_game',
                'games': games
            }
        }
        
    elif message == "2":
        return {
            'type': 'message',
            'message': '''✅ **You chose: Enter two teams manually**

📝 **Enter two NBA teams to analyze:**

💡 **Tip:** You can enter team names like 'Lakers', 'Warriors', 'Celtics', etc.

Enter first team:''',
            'session_state': {'step': 'enter_team1'}
        }
        
    else:
        return {
            'type': 'message',
            'message': '''❌ **Invalid choice.** Please enter **1** or **2**.

**1.** Select from upcoming games
**2.** Enter two teams manually

Enter your choice (1 or 2):''',
            'session_state': session_state
        }

def handle_game_selection(message, session_state):
    """Step 3a: Handle game selection by number"""
    try:
        game_num = int(message)
        games = session_state.get('games', [])
        
        if 1 <= game_num <= len(games):
            selected_game = games[game_num - 1]
            
            return {
                'type': 'message',
                'message': f'''✅ **Selected:** {selected_game['away_team']} @ {selected_game['home_team']}

**Which team do you want to analyze for betting?**
**1.** {selected_game['away_team']} (Away)
**2.** {selected_game['home_team']} (Home)

Enter your choice (1 or 2):''',
                'session_state': {
                    'step': 'choose_team_from_game',
                    'selected_game': selected_game
                }
            }
        else:
            games_count = len(games)
            return {
                'type': 'message',
                'message': f'''❌ **Invalid game number.** Please enter 1-{games_count}.

Select game number (1-{games_count}):''',
                'session_state': session_state
            }
            
    except ValueError:
        games_count = len(session_state.get('games', []))
        return {
            'type': 'message',
            'message': f'''❌ **Invalid input.** Please enter a number.

Select game number (1-{games_count}):''',
            'session_state': session_state
        }

def handle_team_choice_from_game(message, session_state):
    """Step 3b: Handle team choice from selected game"""
    selected_game = session_state.get('selected_game', {})
    
    if message == "1":
        # Away team selected
        return perform_complete_analysis(
            selected_game['away_team'],
            selected_game['home_team'],
            "away",
            "has_home_advantage"
        )
    elif message == "2":
        # Home team selected
        return perform_complete_analysis(
            selected_game['home_team'],
            selected_game['away_team'],
            "home", 
            "has_home_advantage"
        )
    else:
        return {
            'type': 'message',
            'message': f'''❌ **Invalid choice.** Please enter **1** or **2**.

**Which team do you want to analyze for betting?**
**1.** {selected_game['away_team']} (Away)
**2.** {selected_game['home_team']} (Home)

Enter your choice (1 or 2):''',
            'session_state': session_state
        }

def handle_team1_entry(message, session_state):
    """Step 4a: Handle first team entry"""
    team1 = message.strip()
    if not team1:
        return {
            'type': 'message',
            'message': '''❌ **Please enter a team name.**

Enter first team:''',
            'session_state': session_state
        }
    
    return {
        'type': 'message',
        'message': f'''✅ **First team:** {team1}

Enter second team:''',
        'session_state': {
            'step': 'enter_team2',
            'team1': team1
        }
    }

def handle_team2_entry(message, session_state):
    """Step 4b: Handle second team entry"""
    team2 = message.strip()
    team1 = session_state.get('team1', '')
    
    if not team2:
        return {
            'type': 'message',
            'message': '''❌ **Please enter a team name.**

Enter second team:''',
            'session_state': session_state
        }
    
    if team1.lower() == team2.lower():
        return {
            'type': 'message',
            'message': '''❌ **Please enter two different teams.**

Enter second team:''',
            'session_state': session_state
        }
    
    return {
        'type': 'message',
        'message': f'''✅ **Second team:** {team2}

**Which team is playing at home?**
**1.** {team1}
**2.** {team2}

Enter your choice (1 or 2):''',
        'session_state': {
            'step': 'choose_home_team',
            'team1': team1,
            'team2': team2
        }
    }

def handle_home_team_choice(message, session_state):
    """Step 4c: Handle home team selection"""
    team1 = session_state.get('team1', '')
    team2 = session_state.get('team2', '')
    
    if message == "1":
        home_team = team1
    elif message == "2":
        home_team = team2
    else:
        return {
            'type': 'message',
            'message': f'''❌ **Invalid choice.** Please enter **1** or **2**.

**Which team is playing at home?**
**1.** {team1}
**2.** {team2}

Enter your choice (1 or 2):''',
            'session_state': session_state
        }
    
    return {
        'type': 'message',
        'message': f'''✅ **Home team:** {home_team}

🎯 **Which team would you like to analyze for betting?**
**1.** {team1}
**2.** {team2}

Enter your choice (1 or 2):''',
        'session_state': {
            'step': 'choose_team_to_analyze',
            'team1': team1,
            'team2': team2,
            'home_team': home_team
        }
    }

def handle_analysis_team_choice(message, session_state):
    """Step 4d: Handle final team choice for analysis"""
    team1 = session_state.get('team1', '')
    team2 = session_state.get('team2', '')
    home_team = session_state.get('home_team', '')
    
    if message == "1":
        # Analyze team1
        analyzed_team = team1
        opponent_team = team2
        venue = "home" if home_team == team1 else "away"
    elif message == "2":
        # Analyze team2
        analyzed_team = team2
        opponent_team = team1
        venue = "home" if home_team == team2 else "away"
    else:
        return {
            'type': 'message',
            'message': f'''❌ **Invalid choice.** Please enter **1** or **2**.

🎯 **Which team would you like to analyze for betting?**
**1.** {team1}
**2.** {team2}

Enter your choice (1 or 2):''',
            'session_state': session_state
        }
    
    return perform_complete_analysis(analyzed_team, opponent_team, venue, "has_home_advantage")

def perform_complete_analysis(team_to_analyze, opponent, venue, venue_type):
    """Perform the complete analysis exactly like the original chatbot"""
    try:
        # Step 1: Validate and get team stats
        print(f"\n🔍 Fetching data for {team_to_analyze}...")
        team_stats = chatbot.validate_and_get_team_stats(team_to_analyze)
        
        if not team_stats:
            return {
                'type': 'message',
                'message': f'''❌ **Could not find team '{team_to_analyze}' or fetch its data.**

💡 **Try using common team names like:** 'Lakers', 'Warriors', 'Celtics', etc.

Would you like to start over? Send any message to begin again.''',
                'session_state': {'step': 'initial'}
            }
        
        # Step 2: Perform analysis
        print(f"🧠 Analyzing betting recommendation for {team_stats.team_name}...")
        analysis = chatbot.perform_analysis(team_stats, opponent, venue)
        
        if not analysis:
            return {
                'type': 'message',
                'message': '''❌ **Could not complete the analysis.** Please try again.

Send any message to start over.''',
                'session_state': {'step': 'initial'}
            }
        
        # Step 3: Format results exactly like original
        return format_complete_analysis_response(analysis, team_stats, opponent, venue)
        
    except Exception as e:
        print(f"❌ Error in complete analysis: {e}")
        return {
            'type': 'message',
            'message': f'''❌ **Error analyzing teams:** {str(e)}

Send any message to start over.''',
            'session_state': {'step': 'initial'}
        }

def handle_upcoming_games():
    """Handle requests for upcoming games"""
    try:
        games = chatbot.data_fetcher.get_upcoming_games()
        
        if not games:
            return {
                'type': 'message',
                'message': '🏀 **No upcoming games found**\n\nI couldn\'t retrieve the current schedule. You can still ask me to analyze any two teams manually!\n\n**Try asking:**\n• "Analyze Lakers vs Warriors"\n• "Show me Lakers stats"'
            }
        
        # Format games list
        games_text = '🏀 **Upcoming NBA Games:**\n\n'
        for i, game in enumerate(games[:10], 1):  # Limit to 10 games
            date_str = game.date if game.date else "TBD"
            time_str = game.time if game.time else "TBD"
            games_text += f"**{i}.** {game.away_team} @ {game.home_team}\n"
            games_text += f"    📅 {date_str} {time_str}\n\n"
        
        games_text += "Would you like me to analyze any of these matchups?"
        
        return {
            'type': 'message',
            'message': games_text
        }
        
    except Exception as e:
        return {
            'type': 'message',
            'message': '❌ Error fetching upcoming games. Please try again later.'
        }

def handle_team_analysis(message):
    """Handle team vs team analysis requests"""
    try:
        # Extract team names from message
        teams = extract_teams_from_message(message)
        
        if len(teams) < 2:
            return {
                'type': 'message',
                'message': '🏀 **Team Analysis**\n\nPlease specify two teams to analyze. For example:\n• "Analyze Lakers vs Warriors"\n• "Lakers against Celtics"\n• "Compare Nuggets and Suns"'
            }
        
        team1, team2 = teams[0], teams[1]
        
        # Get team statistics (synchronous for now, can be made async later)
        team_stats = chatbot.validate_and_get_team_stats(team1)
        
        if not team_stats:
            return {
                'type': 'message',
                'message': f'❌ **Team not found**: {team1}\n\n💡 **Try using common names like:**\n• Lakers, Warriors, Celtics\n• Heat, Nuggets, Suns\n• Bucks, 76ers, Clippers'
            }
        
        # Perform analysis
        analysis = chatbot.perform_analysis(team_stats, team2, 'neutral')
        
        if analysis:
            return format_analysis_response(team_stats, team2, analysis)
        else:
            return {
                'type': 'message',
                'message': '❌ Could not complete the analysis. Please try again.'
            }
            
    except Exception as e:
        print(f"❌ Error in team analysis: {e}")
        return {
            'type': 'message',
            'message': f'❌ Error analyzing teams: {str(e)}. Please try again.'
        }

def handle_team_stats(message):
    """Handle requests for individual team statistics"""
    try:
        teams = extract_teams_from_message(message)
        
        if not teams:
            return {
                'type': 'message',
                'message': '🏀 **Team Statistics**\n\nPlease specify a team name. For example:\n• "Show me Lakers stats"\n• "Warriors statistics"\n• "Celtics record"'
            }
        
        team_name = teams[0]
        team_stats = chatbot.validate_and_get_team_stats(team_name)
        
        if not team_stats:
            return {
                'type': 'message',
                'message': f'❌ **Team not found**: {team_name}\n\n💡 **Try using common names like:**\n• Lakers, Warriors, Celtics\n• Heat, Nuggets, Suns\n• Bucks, 76ers, Clippers'
            }
        
        return format_team_stats_response(team_stats)
        
    except Exception as e:
        return {
            'type': 'message',
            'message': '❌ Error getting team statistics. Please try again.'
        }

def handle_help_request():
    """Handle help requests"""
    return {
        'type': 'message',
        'message': '''🏀 **NBA Betting Expert - How I can help:**

**🎯 Team Analysis**
• "Analyze Lakers vs Warriors"
• "Compare Celtics and Heat"

**📊 Team Statistics**
• "Show me Lakers stats"
• "Warriors record and performance"

**📅 Upcoming Games**
• "Show upcoming games"
• "What games are today?"

**🎲 Betting Recommendations**
• "Should I bet on Lakers?"
• "Risk assessment for Warriors"

**💡 Tips:**
• Use common team names (Lakers, Warriors, etc.)
• I provide real-time statistics and AI-powered analysis
• All recommendations include risk assessment
• Ask about specific matchups for detailed analysis'''
    }

def handle_general_query(message):
    """Handle general queries"""
    return {
        'type': 'message',
        'message': '''🏀 **Welcome to NBA Betting Expert!**

I can help you with:
• **Team analysis and comparisons**
• **Real-time NBA statistics**
• **Betting recommendations with risk assessment**
• **Upcoming game schedules**

**Try asking:**
• "Analyze Lakers vs Warriors"
• "Show upcoming games"
• "Help" for more options

What would you like to know?'''
    }

def extract_teams_from_message(message):
    """Extract team names from user message"""
    # Common NBA team names and abbreviations with better mapping
    team_mapping = {
        'lakers': 'Lakers', 'la lakers': 'Lakers', 'los angeles lakers': 'Lakers',
        'warriors': 'Warriors', 'golden state': 'Warriors', 'gsw': 'Warriors',
        'celtics': 'Celtics', 'boston': 'Celtics', 'bos': 'Celtics',
        'heat': 'Heat', 'miami': 'Heat', 'mia': 'Heat',
        'nuggets': 'Nuggets', 'denver': 'Nuggets', 'den': 'Nuggets',
        'suns': 'Suns', 'phoenix': 'Suns', 'phx': 'Suns',
        'bucks': 'Bucks', 'milwaukee': 'Bucks', 'mil': 'Bucks',
        'sixers': '76ers', '76ers': '76ers', 'philadelphia': '76ers', 'phi': '76ers',
        'clippers': 'Clippers', 'la clippers': 'Clippers', 'lac': 'Clippers',
        'mavericks': 'Mavericks', 'mavs': 'Mavericks', 'dallas': 'Mavericks', 'dal': 'Mavericks',
        'rockets': 'Rockets', 'houston': 'Rockets', 'hou': 'Rockets',
        'spurs': 'Spurs', 'san antonio': 'Spurs', 'sas': 'Spurs',
        'thunder': 'Thunder', 'okc': 'Thunder', 'oklahoma city': 'Thunder',
        'blazers': 'Trail Blazers', 'trail blazers': 'Trail Blazers', 'portland': 'Trail Blazers', 'por': 'Trail Blazers',
        'jazz': 'Jazz', 'utah': 'Jazz', 'uta': 'Jazz',
        'kings': 'Kings', 'sacramento': 'Kings', 'sac': 'Kings',
        'grizzlies': 'Grizzlies', 'memphis': 'Grizzlies', 'mem': 'Grizzlies',
        'pelicans': 'Pelicans', 'new orleans': 'Pelicans', 'nop': 'Pelicans',
        'hawks': 'Hawks', 'atlanta': 'Hawks', 'atl': 'Hawks',
        'hornets': 'Hornets', 'charlotte': 'Hornets', 'cha': 'Hornets',
        'magic': 'Magic', 'orlando': 'Magic', 'orl': 'Magic',
        'wizards': 'Wizards', 'washington': 'Wizards', 'was': 'Wizards',
        'pistons': 'Pistons', 'detroit': 'Pistons', 'det': 'Pistons',
        'pacers': 'Pacers', 'indiana': 'Pacers', 'ind': 'Pacers',
        'cavaliers': 'Cavaliers', 'cavs': 'Cavaliers', 'cleveland': 'Cavaliers', 'cle': 'Cavaliers',
        'raptors': 'Raptors', 'toronto': 'Raptors', 'tor': 'Raptors',
        'nets': 'Nets', 'brooklyn': 'Nets', 'bkn': 'Nets',
        'knicks': 'Knicks', 'new york': 'Knicks', 'nyk': 'Knicks',
        'bulls': 'Bulls', 'chicago': 'Bulls', 'chi': 'Bulls',
        'timberwolves': 'Timberwolves', 'wolves': 'Timberwolves', 'minnesota': 'Timberwolves', 'min': 'Timberwolves'
    }
    
    message_lower = message.lower()
    found_teams = []
    
    # Sort by length (longest first) to match longer names first
    sorted_teams = sorted(team_mapping.keys(), key=len, reverse=True)
    
    for team_key in sorted_teams:
        if team_key in message_lower and team_mapping[team_key] not in found_teams:
            found_teams.append(team_mapping[team_key])
            if len(found_teams) >= 2:  # Stop after finding 2 teams
                break
    
    return found_teams

def format_analysis_response(team_stats, opponent, analysis):
    """Format the analysis results for the frontend"""
    try:
        # Generate summary using chatbot method
        summary = chatbot._generate_summary_reasons(analysis, team_stats, 'neutral', opponent)
        
        return {
            'type': 'analysis',
            'data': {
                'team_name': team_stats.team_name,
                'opponent': opponent,
                'recommendation': analysis.recommendation,
                'confidence': f"{analysis.confidence:.0%}",
                'risk_level': analysis.risk_level.title(),
                'team_record': f"{team_stats.wins}-{team_stats.losses}",
                'win_percentage': f"{team_stats.win_percentage:.1%}",
                'ppg': f"{team_stats.points_per_game:.1f}",
                'streak': getattr(team_stats, 'streak', 'N/A'),
                'reasoning': analysis.reasoning[:5],  # Limit to 5 reasons
                'summary': summary,
                'bayesian_confidence': f"{analysis.bayesian_probability:.1%}" if hasattr(analysis, 'bayesian_probability') else "N/A"
            }
        }
    except Exception as e:
        print(f"❌ Error formatting analysis: {e}")
        return {
            'type': 'message',
            'message': 'Analysis completed but there was an error formatting the results.'
        }

def format_team_stats_response(team_stats):
    """Format team statistics for display"""
    try:
        stats_text = f'''📊 **{team_stats.team_name} Statistics**

**Overall Record:** {team_stats.wins}-{team_stats.losses} ({team_stats.win_percentage:.1%})

**Scoring:**
• Points per game: {team_stats.points_per_game:.1f}
• Points allowed: {team_stats.opponent_points_per_game:.1f}

**Records:**'''

        if hasattr(team_stats, 'home_record') and team_stats.home_record:
            stats_text += f"\n• Home: {team_stats.home_record}"
        
        if hasattr(team_stats, 'away_record') and team_stats.away_record:
            stats_text += f"\n• Away: {team_stats.away_record}"            
        if hasattr(team_stats, 'last_10_games') and team_stats.last_10_games:
            stats_text += f"\n• Last 10: {team_stats.last_10_games}"
            
        if hasattr(team_stats, 'streak') and team_stats.streak:
            stats_text += f"\n\n**Current Streak:** {team_stats.streak}"
            
        if team_stats.unavailable_players:
            stats_text += f"\n\n**Unavailable Players:**\n"
            for player in team_stats.unavailable_players[:5]:  # Limit to 5 players
                stats_text += f"• {player}\n"
        
        stats_text += "\n\n💡 Want analysis? Try: \"Analyze [team] vs [opponent]\""
        
        return {
            'type': 'message',
            'message': stats_text
        }
        
    except Exception as e:
        return {
            'type': 'message',
            'message': 'Error formatting team statistics.'
        }

def format_complete_analysis_response(analysis, team_stats, opponent, venue):
    """Format the complete analysis results exactly like the original chatbot display_analysis_results"""
    try:
        # Generate detailed summary reasons using the chatbot method
        summary_reasons = chatbot._generate_summary_reasons(analysis, team_stats, venue, opponent)
        
        # Get detailed Bayesian explanation if available
        try:
            bayesian_explanation = chatbot.bayesian_analyzer.explain_inference(team_stats, venue)
        except:
            bayesian_explanation = "Bayesian analysis completed with standard inference."
        
        # Format the complete analysis result - simplified for web interface
        try:
            summary_reasons = chatbot._generate_summary_reasons(analysis, team_stats, venue, opponent)
        except:
            summary_reasons = "Analysis completed based on team performance metrics."        # Build team info lines
        team_info_lines = []
        if hasattr(team_stats, 'last_10_games') and team_stats.last_10_games:
            team_info_lines.append(f"• Last 10: {team_stats.last_10_games}")
        if hasattr(team_stats, 'streak') and team_stats.streak:
            team_info_lines.append(f"• Streak: {team_stats.streak}")
        if hasattr(team_stats, 'home_record') and team_stats.home_record:
            team_info_lines.append(f"• Home: {team_stats.home_record}")
        if hasattr(team_stats, 'away_record') and team_stats.away_record:
            team_info_lines.append(f"• Away: {team_stats.away_record}")
        
        team_info_text = "\n".join(team_info_lines)
        
        # Build triggered rules text
        rule_count = len(analysis.triggered_rules) if analysis.triggered_rules else 0
        rules_list = analysis.triggered_rules[:3] if analysis.triggered_rules else ["No specific rules triggered"]
        rules_text = "\n".join([f"• {rule}" for rule in rules_list])
        
        # Build key factors text
        factors_list = analysis.reasoning[:5] if analysis.reasoning else ["Standard performance metrics"]
        factors_text = "\n".join([f"• {reason}" for reason in factors_list])
        
        # Build bayesian confidence
        bayesian_conf = f"{analysis.bayesian_probability:.1%}" if hasattr(analysis, 'bayesian_probability') else "N/A"
        
        # Build risk emoji
        risk_emoji = "🟢" if analysis.risk_level == "low" else "🟡" if analysis.risk_level == "medium" else "🔴"
        
        # Build recommendation emoji and text
        rec_emoji = "✅" if analysis.recommendation == "safe" else "⚠️"
        final_advice = "💡 The analysis suggests favorable conditions for this bet." if analysis.recommendation == "safe" else "⚠️ The analysis suggests caution with this bet due to identified risk factors."
            
        return {
            'type': 'message',
            'message': f'''✅ **COMPLETE ANALYSIS RESULTS**

**🎯 ANALYSIS FOR: {team_stats.team_name}**
**🆚 OPPONENT:** {opponent}
**🏟️ VENUE:** {venue.upper()}

**🎯 RECOMMENDATION**
{rec_emoji} **{analysis.recommendation.upper()} BET**
**Risk Level:** {analysis.risk_level.upper()}
**Confidence:** {analysis.confidence:.1%}

**📊 TEAM INFORMATION**
• Record: {team_stats.wins}-{team_stats.losses} ({team_stats.win_percentage:.1%})
• Scoring: {team_stats.points_per_game:.1f} PPG
• Defense: {team_stats.opponent_points_per_game:.1f} points allowed
{team_info_text}

**🧠 EXPERT SYSTEM ANALYSIS**
Triggered Rules: {rule_count}
{rules_text}

**Key Factors:**
{factors_text}

**📈 BAYESIAN ANALYSIS**
Confidence Level: {bayesian_conf}

**📋 SUMMARY**
{risk_emoji} {summary_reasons}

{final_advice}

Send any message to start a new analysis.''',
            'session_state': {'step': 'initial'}
        }
        
    except Exception as e:
        print(f"❌ Error formatting complete analysis: {e}")
        # Fallback to simple message format
        return {
            'type': 'message',
            'message': f'''✅ **Analysis Complete!**

**{team_stats.team_name}** vs **{opponent}** ({'Home' if venue == 'home' else 'Away'})

**Recommendation:** {analysis.recommendation.upper()} BET
**Risk Level:** {analysis.risk_level.upper()}
**Confidence:** {analysis.confidence:.1%}

**Team Record:** {team_stats.wins}-{team_stats.losses} ({team_stats.win_percentage:.1%})
**Scoring:** {team_stats.points_per_game:.1f} PPG, {team_stats.opponent_points_per_game:.1f} allowed

Send any message to start a new analysis.''',
            'session_state': {'step': 'initial'}
        }

@app.route('/health')
def health_check():
    """Health check endpoint for deployment monitoring"""
    return jsonify({
        'status': 'healthy',
        'service': 'NBA Sports Betting Expert Web Server',
        'timestamp': time.time()
    })

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    try:
        # Test if chatbot can be initialized
        test_chatbot = NBAChatbot()
        return jsonify({
            'status': 'operational',
            'api_version': '1.0',
            'services': {
                'chatbot': 'available',
                'nba_data': 'available'
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'degraded',
            'error': str(e),
            'services': {
                'chatbot': 'error',
                'nba_data': 'unknown'
            }
        }), 500

if __name__ == '__main__':
    # Configuration for deployment
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Get configuration from environment variables
    PORT = int(os.environ.get("PORT", 5000))
    HOST = os.environ.get("HOST", "0.0.0.0")
    
    print("🏀 Starting NBA Betting Expert Web Interface...")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        app.run(debug=False, host=HOST, port=PORT)
    except KeyboardInterrupt:
        print("\n👋 NBA Betting Expert Web Server stopped.")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print(f"Make sure port {PORT} is not already in use.")
