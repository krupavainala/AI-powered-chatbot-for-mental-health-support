# app/quotes.py


motivational_quotes = [
    "Believe in yourself!",
    "You are stronger than you think.",
    "Every day is a new opportunity.",
    "Keep pushing forward.",
    "You got this!",
    "Difficult roads often lead to beautiful destinations.",
    "It’s okay to not be okay.",
    "One step at a time.",
    "You are enough, just as you are.",
    "Your feelings are valid.",
    "Be proud of how far you’ve come.",
    "You are capable of amazing things.",
    "It’s a bad day, not a bad life.",
    "Progress, not perfection.",
    "You are not alone.",
    "This too shall pass.",
    "Healing takes time, and that’s okay.",
    "Your journey is unique.",
    "You deserve happiness.",
    "You have the power to create change.",
    "Be gentle with yourself.",
    "Start where you are. Use what you have. Do what you can.",
    "Small steps lead to big results.",
    "Rest is productive.",
    "Your mind is a garden—nurture it with kindness.",
    "One moment at a time.",
    "You’ve survived 100% of your worst days.",
    "Let your courage be stronger than your fear.",
    "You are doing better than you think.",
    "Don’t give up—you are closer than you think.",
    "Breathe. Relax. You are in control.",
    "You are worthy of love and care.",
    "Self-care is never selfish.",
    "Focus on progress, not perfection.",
    "Storms make trees take deeper roots.",
    "Growth begins where comfort ends.",
    "You’ve got what it takes.",
    "You are more than your struggles.",
    "Your voice matters.",
    "Keep showing up.",
    "Strength grows in the moments you think you can't go on but you keep going anyway.",
    "Your pace is perfect for your path.",
    "Every sunrise brings a new hope.",
    "You have a 100% success rate at surviving bad days.",
    "The comeback is always stronger than the setback.",
    "Feel it. Face it. Heal from it.",
    "You don’t need to have it all figured out.",
    "Your life is not a race.",
    "There is light, even in the darkest of times.",
    "Courage doesn’t always roar. Sometimes it’s a whisper.",
    "You are a work in progress, and that’s okay.",
    "There’s no shame in asking for help.",
    "Healing isn’t linear.",
    "Your story is not over.",
    "Let go of what you can’t control.",
    "Every effort counts.",
    "You have permission to pause.",
    "Be proud of small victories.",
    "Growth is painful, but so is staying stuck.",
    "You are not a burden.",
    "Your mental health matters.",
    "It’s brave to feel your feelings.",
    "You deserve inner peace.",
    "Recovery is possible.",
    "You are doing the best you can.",
    "Choose hope, even when it’s hard.",
    "Trust the timing of your life.",
    "Don’t compare your chapter 1 to someone else’s chapter 10.",
    "The only way out is through.",
    "You’re doing better than you were yesterday.",
    "You have the strength within you.",
    "Your dreams are valid.",
    "Keep hope in your heart.",
    "Choose yourself daily.",
    "You are enough.",
    "One day at a time.",
    "Every step forward is progress.",
    "You are growing even when it feels like you’re not.",
    "Trust yourself.",
    "Your presence matters.",
    "Be kind to your mind.",
    "Your past does not define you.",
    "Let today be a new beginning.",
    "Peace begins with you.",
    "You are not broken.",
    "Your courage inspires others.",
    "You can always begin again.",
    "Celebrate your progress.",
    "You are not weak for struggling.",
    "It’s okay to rest.",
    "Your worth is not measured by productivity.",
    "Hope is stronger than fear.",
    "You can rewrite your story.",
    "Breathe deeply. You are safe here.",
    "You are more than enough.",
    "It’s okay to start over.",
    "Your best is good enough.",
    "Your presence brings light.",
    "Even the darkest night will end and the sun will rise.",
    "Take time to recharge.",
    "You’re allowed to outgrow people, places, and versions of yourself.",
    "Kindness to yourself is a revolutionary act.",
    "Be patient with your progress."
]
calming_exercises = [
    "Focus on your breath. Inhale deeply for 4 seconds, hold for 4 seconds, then exhale for 4 seconds. Repeat until you feel calm.",
    "Let’s try progressive muscle relaxation. Start by tensing your feet, hold for a few seconds, and then release. Slowly move up your body—legs, abdomen, arms—tense and release each muscle group.",
    "Try box breathing: Inhale for 4 seconds, hold for 4, exhale for 4, and hold again for 4. Repeat this cycle for 2-3 minutes.",
    "Take a moment to reflect on your feelings. Try grounding yourself by identifying 5 things you can see, 4 things you can touch, 3 things you can hear, 2 things you can smell, and 1 thing you can taste.",
    "Focus on being present. Look around and notice the details of your surroundings. Take a few slow, deep breaths to center yourself.",
    "Imagine a peaceful place, whether it's a quiet beach, forest, or mountain. Picture yourself there, feeling calm and relaxed."
    "Let’s focus on grounding. Find 5 things you can see, 4 things you can touch, 3 things you can hear, 2 things you can smell, and 1 thing you can taste. This helps to bring you into the present moment."
    "Try box breathing: Inhale for 4 seconds, hold for 4, exhale for 4, and hold again for 4. Repeat this cycle for 2-3 minutes."
    "Put your hand over your heart and say to yourself: 'I am doing the best I can, and that’s enough. It’s okay to take it one step at a time.'"
    "Repeat these affirmations: 'I am calm. I am strong. I am in control. I can handle this moment.' Say them out loud or quietly to yourself."
    "Try this breathing exercise: Breathe in for 5 seconds, hold for 5, and breathe out for 5. Focus only on your breath and repeat for a few minutes."
    "Sit quietly and listen. Focus only on sounds around you—whether it’s the hum of the air, the rustling of leaves, or any soothing sound. Let yourself be absorbed by it."
"Close your eyes and imagine your peaceful place—a quiet beach, a serene forest, or a cozy room. Visualize the sounds, smells, and feelings you associate with this place, and let it bring you calm."
"If you can, try soaking your hands or feet in warm water. The warmth can help relax your muscles and soothe your mind."
"Take a moment to write about how you’re feeling. It can help to get your thoughts down on paper and reflect on your emotions."

]
import emoji
import re

# Emoji to mood mapping
emoji_mood_map = {
    "😊": "happy",
    "😢": "sad",
    "😡": "angry",
    "😰": "anxious",
    "😴": "tired",
    "❤️": "love",
    "😞": "disappointed",
    "😔": "sad",
    "😃": "happy",
    "😩": "stressed",
    "😕": "confused",
    "😇": "hopeful",
    "😭": "crying",
    "😤": "frustrated",
    "🤗": "comforted",
    "🤔": "thoughtful",
    "😐": "neutral",
    "😱": "scared",
    "😌": "relaxed",
    "🤩": "excited"
}   
def detect_mood_from_emoji(text):
    for emoji, mood in emoji_mood_map.items():
        if emoji in text:
            return mood
    return None
# Mood to response mapping
mood_responses = {
    "happy": "I'm glad to see you're feeling happy! Keep that positive energy shining 😊",
    "sad": "It's okay to feel sad sometimes. I'm here to listen and support you.",
    "angry": "Feeling angry is natural. Try some deep breaths to help calm down.",
    "anxious": "Anxiety can be tough. Let's focus on calming thoughts together.",
    "tired": "Make sure to get some rest and take care of yourself.",
    "love": "Love is beautiful! Remember, you are loved and appreciated.",
    "disappointed": "Disappointments happen, but every day is a new chance for better moments.",
    "stressed": "Stress is heavy—let's try to relax and take one step at a time.",
    "confused": "It's okay to feel confused. Take your time, clarity will come.",
    "hopeful": "Hope is a powerful feeling. Keep holding on to it.",
    "crying": "It's alright to cry. Let your emotions flow and heal.",
    "frustrated": "Frustration is tough. Let's find ways to release it healthily.",
    "comforted": "I'm glad you feel comforted. You're not alone.",
    "thoughtful": "Thinking things through is important. I'm here as you reflect.",
    "neutral": "Sometimes feeling neutral is okay. I'm here whenever you need me.",
    "scared": "Fear can feel overwhelming. You're safe here.",
    "relaxed": "Relaxation is wonderful. Keep embracing peace.",
    "excited": "Excitement is contagious! Tell me more about it.",
}


