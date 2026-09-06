"""
PyMaster Comic Engine — AI-powered comic-style educational content generator.
Integrates patterns from:
- OpenMAIC: Multi-agent classroom dialog (Teacher + Student characters)
- OpenViking: Persistent memory for learning context
- PilotDeck: Agent orchestration for content generation
- DeerFlow: SKILL.md-based workflow orchestration
"""
import json
import os
import hashlib
import time
import re
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional

# ── Data Models ───────────────────────────────────────────

@dataclass
class ComicPanel:
    panel_id: int
    character: str          # "teacher", "student", "narrator"
    character_name: str
    avatar: str             # emoji
    dialog: str
    expression: str         # "explaining", "thinking", "surprised", "happy", "questioning"
    scene: str
    knowledge_bite: str     # the key knowledge conveyed in this panel

@dataclass
class ComicScript:
    title: str
    chapter_title: str
    kp_title: str
    panels: list  # list of ComicPanel
    total_panels: int
    generated_at: str


class ComicEngine:
    """Generates comic-style educational scripts from knowledge points."""

    CHARACTERS = {
        "teacher": {
            "name": "蛇蛇老师",
            "avatar": "🐍",
            "role": "Python 专家，耐心幽默",
            "style": "用生动的比喻解释概念，喜欢举有趣的例子"
        },
        "student": {
            "name": "小码",
            "avatar": "🐣",
            "role": "好奇的学生，正在学编程",
            "style": "会提出初学者的常见疑问，有时会恍然大悟"
        },
        "narrator": {
            "name": "旁白",
            "avatar": "📖",
            "role": "场景叙述者",
            "style": "简洁地描述场景转换和背景信息"
        }
    }

    EXPRESSIONS = {
        "explaining": "认真讲解中",
        "thinking": "思考中",
        "surprised": "感到惊讶",
        "happy": "开心微笑",
        "questioning": "举手提问",
        "excited": "兴奋激动",
        "inspired": "恍然大悟"
    }

    SCENES = ["classroom", "coding_lab", "thought_bubble", "whiteboard", "computer_screen"]

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.api_key = self.config.get("api_key") or os.environ.get("OPENAI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
        self.api_base = self.config.get("api_base") or os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = self.config.get("model") or os.environ.get("COMIC_MODEL", "gpt-4o")
        self.provider = self.config.get("provider") or os.environ.get("COMIC_PROVIDER", "openai")

    def is_available(self) -> bool:
        return bool(self.api_key)

    def generate(self, chapter_title: str, kp_title: str, kp_content: str,
                 chapter_id: int, kp_index: int) -> ComicScript:
        """
        Generate a comic script from a knowledge point.
        Falls back to template-based generation if no API key is configured.
        """
        if self.is_available():
            return self._ai_generate(chapter_title, kp_title, kp_content, chapter_id, kp_index)
        else:
            return self._template_generate(chapter_title, kp_title, kp_content, chapter_id, kp_index)

    def _ai_generate(self, chapter_title: str, kp_title: str, kp_content: str,
                     chapter_id: int, kp_index: int) -> ComicScript:
        """Use AI API to generate a rich comic script."""
        import urllib.request
        import urllib.error

        system_prompt = f"""你是一个教育漫画剧本创作AI。你的任务是把知识点转化为有趣的漫画对话。

设定：
- 老师角色：{self.CHARACTERS['teacher']['name']}（{self.CHARACTERS['teacher']['avatar']}），{self.CHARACTERS['teacher']['role']}。风格：{self.CHARACTERS['teacher']['style']}
- 学生角色：{self.CHARACTERS['student']['name']}（{self.CHARACTERS['student']['avatar']}），{self.CHARACTERS['student']['role']}。风格：{self.CHARACTERS['student']['style']}

表情选项：{', '.join(self.EXPRESSIONS.keys())}
场景选项：{', '.join(self.SCENES)}

生成规则：
1. 创作4-8格漫画，每格包含角色对话
2. 开头由老师引入话题，中间穿插学生的提问和恍然大悟
3. 每格对话控制在20-60字，简明生动
4. 使用比喻和故事化的方式讲解
5. 最后一格做知识点总结
6. 对话要适合青少年阅读，生动有趣但不幼稚

返回严格的JSON格式（不要markdown包裹）:
{{
  "panels": [
    {{
      "character": "teacher|student|narrator",
      "dialog": "对话内容",
      "expression": "explaining|thinking|surprised|happy|questioning|excited|inspired",
      "scene": "classroom|coding_lab|thought_bubble|whiteboard|computer_screen",
      "knowledge_bite": "这一格传递的知识点摘要"
    }}
  ]
}}"""

        user_prompt = f"""请为以下Python知识点创作漫画讲解：

课程章节：{chapter_title}
知识点：{kp_title}
知识点内容：
{kp_content[:1500]}

请创作生动有趣的漫画对话剧本。"""

        try:
            # Try OpenAI-compatible API first
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.8,
                "max_tokens": 2000
            }

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            req = urllib.request.Request(
                f"{self.api_base}/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                content = result["choices"][0]["message"]["content"]

            # Parse the JSON from AI response
            content = content.strip()
            if content.startswith("```"):
                content = re.sub(r'^```\w*\n?', '', content)
                content = re.sub(r'\n?```$', '', content)

            data = json.loads(content)
            return self._build_script(chapter_title, kp_title, data.get("panels", []))

        except Exception as e:
            print(f"[ComicEngine] AI generation failed: {e}, falling back to template")
            return self._template_generate(chapter_title, kp_title, kp_content, chapter_id, kp_index)

    def _template_generate(self, chapter_title: str, kp_title: str, kp_content: str,
                           chapter_id: int, kp_index: int) -> ComicScript:
        """
        Template-based comic generation when AI API is unavailable.
        Uses smart content extraction to create engaging comic panels.
        """
        T = self.CHARACTERS["teacher"]
        S = self.CHARACTERS["student"]
        N = self.CHARACTERS["narrator"]

        panels = []

        # Panel 1: Opening scene - Teacher introduces the topic
        panels.append(ComicPanel(
            panel_id=1,
            character="teacher",
            character_name=T["name"],
            avatar=T["avatar"],
            dialog=f"同学们好！今天我们来学习「{kp_title}」。这可是Python编程中非常有趣的一部分哦！",
            expression="happy",
            scene="classroom",
            knowledge_bite=f"课程开始：{kp_title}"
        ))

        # Panel 2: Student shows curiosity
        panels.append(ComicPanel(
            panel_id=2,
            character="student",
            character_name=S["name"],
            avatar=S["avatar"],
            dialog=f"老师老师！{self._generate_student_question(kp_title)}",
            expression="questioning",
            scene="classroom",
            knowledge_bite=f"学生提问关于{kp_title}"
        ))

        # Extract key points from content and create teaching panels
        key_points = self._extract_key_points(kp_content)

        for i, point in enumerate(key_points):
            panels.append(ComicPanel(
                panel_id=len(panels) + 1,
                character="teacher",
                character_name=T["name"],
                avatar=T["avatar"],
                dialog=self._format_teacher_dialog(point),
                expression="explaining",
                scene="whiteboard",
                knowledge_bite=point[:80]
            ))

            # Student reaction
            if i < len(key_points) - 1:
                panels.append(ComicPanel(
                    panel_id=len(panels) + 1,
                    character="student",
                    character_name=S["name"],
                    avatar=S["avatar"],
                    dialog=self._generate_student_reaction(point),
                    expression=["thinking", "surprised", "inspired"][i % 3],
                    scene="thought_bubble",
                    knowledge_bite="学生消化理解中"
                ))

        # Teacher shows a code example if available
        code_block = self._extract_code(kp_content)
        if code_block:
            panels.append(ComicPanel(
                panel_id=len(panels) + 1,
                character="teacher",
                character_name=T["name"],
                avatar=T["avatar"],
                dialog=f"来，我们看一个实际例子：\n{code_block[:120]}",
                expression="explaining",
                scene="computer_screen",
                knowledge_bite="代码示例演示"
            ))

        # Student has an "aha!" moment
        panels.append(ComicPanel(
            panel_id=len(panels) + 1,
            character="student",
            character_name=S["name"],
            avatar=S["avatar"],
            dialog=self._generate_aha_moment(kp_title),
            expression="inspired",
            scene="thought_bubble",
            knowledge_bite="学生恍然大悟"
        ))

        # Closing panel - Summary
        panels.append(ComicPanel(
            panel_id=len(panels) + 1,
            character="teacher",
            character_name=T["name"],
            avatar=T["avatar"],
            dialog=self._generate_summary(kp_title, key_points),
            expression="happy",
            scene="classroom",
            knowledge_bite=f"知识点总结：{kp_title}"
        ))

        return self._build_script(chapter_title, kp_title, panels)

    def _build_script(self, chapter_title: str, kp_title: str, panels: list) -> ComicScript:
        """Build a ComicScript from panel data."""
        result_panels = []
        for i, p in enumerate(panels):
            if isinstance(p, ComicPanel):
                result_panels.append(p)
            else:
                char = p.get("character", "teacher")
                char_info = self.CHARACTERS.get(char, self.CHARACTERS["teacher"])
                result_panels.append(ComicPanel(
                    panel_id=i + 1,
                    character=char,
                    character_name=p.get("character_name", char_info["name"]),
                    avatar=p.get("avatar", char_info["avatar"]),
                    dialog=p.get("dialog", ""),
                    expression=p.get("expression", "explaining"),
                    scene=p.get("scene", "classroom"),
                    knowledge_bite=p.get("knowledge_bite", "")
                ))

        return ComicScript(
            title=f"「{kp_title}」漫画讲解",
            chapter_title=chapter_title,
            kp_title=kp_title,
            panels=result_panels,
            total_panels=len(result_panels),
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

    def _extract_key_points(self, content: str) -> list:
        """Extract key learning points from HTML content."""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', content)
        text = re.sub(r'\s+', ' ', text).strip()

        points = []
        # Try to get sentences that look like key points
        sentences = re.split(r'[。；]', text)
        for s in sentences:
            s = s.strip()
            if len(s) > 10 and len(s) < 120:
                # Prefer sentences with strong indicators
                if any(kw in s for kw in ['是', '用', '可以', '需要', '通过', '包含', '支持', '称为']):
                    points.append(s + '。')

        if not points:
            # Fallback: just split into chunks
            chunks = [text[i:i+100] for i in range(0, min(len(text), 400), 100)]
            points = [c.strip() for c in chunks if len(c.strip()) > 10]

        return points[:4]  # Max 4 key points for comic format

    def _extract_code(self, content: str) -> Optional[str]:
        """Extract first code block from HTML content."""
        match = re.search(r'<code>(.*?)</code>', content, re.DOTALL)
        if match:
            code = match.group(1).strip()
            return code[:150]
        match = re.search(r'<pre><code>(.*?)</code></pre>', content, re.DOTALL)
        if match:
            code = match.group(1).strip()
            return code[:150]
        return None

    def _format_teacher_dialog(self, point: str) -> str:
        """Format a key point as teacher dialog with engaging style."""
        metaphors = ["可以把它想象成", "打个比方", "就像", "简单来说就是", "你可以理解为"]
        import random
        metaphor = random.choice(metaphors)
        # Make it conversational
        point = re.sub(r'^(Python|它|其)', '', point).strip('，。')
        return f"好问题！{metaphor}，{point}。"

    def _generate_student_question(self, kp_title: str) -> str:
        questions = [
            f"「{kp_title}」到底是什么呀？能举个例子吗？",
            f"为什么要学「{kp_title}」呢？它有什么用？",
            f"老师！「{kp_title}」在实际编程中怎么用呢？",
            f"我听说「{kp_title}」很重要，但是不太理解...",
        ]
        import random
        return random.choice(questions)

    def _generate_student_reaction(self, point: str) -> str:
        reactions = [
            "喔~原来是这样！我好像有点明白了！",
            "这么一说确实很有道理！",
            "嗯...我再想想...好像是这么回事！",
            "哇！这个知识点好有用！"
        ]
        import random
        return random.choice(reactions)

    def _generate_aha_moment(self, kp_title: str) -> str:
        moments = [
            f"啊！我懂了！原来「{kp_title}」是这个意思！",
            f"豁然开朗！之前一直搞不清楚这个概念，现在全明白了！",
            f"原来如此！感觉编程又变简单了一点~",
            f"太棒了，我又学会了一个新知识点！"
        ]
        import random
        return random.choice(moments)

    def _generate_summary(self, kp_title: str, points: list) -> str:
        if points:
            first_point = re.sub(r'<[^>]+>', '', points[0])[:40]
            return f"总结一下：今天我们学了「{kp_title}」。记住哦——{first_point}... 大家可以在练习中巩固一下！"
        return f"好啦！「{kp_title}」就讲到这里。记住核心概念，多动手练习，你一定可以掌握的！"


# ── Memory System (OpenViking-inspired) ────────────────────

class ComicMemory:
    """
    Persistent memory for tracking which comics students have viewed.
    Inspired by OpenViking's tiered context loading (L0/L1/L2).
    - L0: Comic view count (always loaded)
    - L1: Recently viewed topics (loaded on request)
    - L2: Full interaction history (loaded on demand)
    """

    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.memory_file = os.path.join(data_dir, 'comic_memory.json')
        os.makedirs(data_dir, exist_ok=True)

    def load(self) -> dict:
        if not os.path.exists(self.memory_file):
            return {}
        with open(self.memory_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save(self, data: dict):
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def record_view(self, username: str, chapter_id: int, kp_index: int, kp_title: str):
        """Record that a student viewed a comic."""
        memory = self.load()
        if username not in memory:
            memory[username] = {"views": [], "favorites": [], "total_views": 0}

        user_mem = memory[username]
        user_mem["total_views"] += 1
        user_mem["views"].append({
            "chapter_id": chapter_id,
            "kp_index": kp_index,
            "kp_title": kp_title,
            "viewed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        # Keep only last 50 views
        if len(user_mem["views"]) > 50:
            user_mem["views"] = user_mem["views"][-50:]

        self.save(memory)

    def get_stats(self, username: str) -> dict:
        """Get comic viewing stats (L0: always loaded)."""
        memory = self.load()
        user_mem = memory.get(username, {})
        views = user_mem.get("views", [])
        return {
            "total_views": user_mem.get("total_views", 0),
            "recent_topics": [v["kp_title"] for v in views[-5:]],
            "unique_topics": len(set(v["kp_title"] for v in views)),
            "last_viewed": views[-1]["viewed_at"] if views else None
        }

    def get_recommendations(self, username: str, all_kps: list) -> list:
        """Generate personalized recommendations (L1: loaded on request)."""
        memory = self.load()
        user_mem = memory.get(username, {})
        viewed = {v["kp_title"] for v in user_mem.get("views", [])}

        # Recommend unviewed topics
        unviewed = [kp for kp in all_kps if kp["title"] not in viewed]
        return unviewed[:3]
