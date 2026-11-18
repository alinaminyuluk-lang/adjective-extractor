from pathlib import Path
import gradio as gr
from adjectives import extract_adjectives, TextValidationError


def load_sample(filename: str) -> str:
    path = Path("data") / filename
    return path.read_text(encoding="utf-8") if path.exists() else ""


def analyze_ui(text: str):
    try:
        result = extract_adjectives(text)
    except TextValidationError as err:
        raise gr.Error(str(err))
    except Exception as err:
        raise gr.Error(f"Непередбачена помилка обробки: {err}")

    table_rows = [
        [
            idx + 1,
            item["word"],
            item["lemma"],
            item["gender"],
            item["number"],
            item["case"],
        ]
        for idx, item in enumerate(result["adjectives"])
    ]

    summary = (
        f"### Результати аналізу\n"
        f"- **Усього слів у тексті:** {result['total_words']}\n"
        f"- **Знайдено прикметників:** {result['adj_count']}\n"
        f"- **Частка прикметників:** {result['percentage']}%"
    )

    return result["highlighted"], summary, table_rows


custom_css = """
.gradio-container {
    max-width: 1050px !important;
    margin: 0 auto !important;
    font-family: 'Segoe UI', Tahoma, sans-serif;
}
#header-banner {
    background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
    color: white;
    padding: 22px;
    border-radius: 12px;
    margin-bottom: 16px;
}
#header-banner h1, #header-banner p {
    color: white !important;
    margin: 0;
}
"""

with gr.Blocks(theme=gr.themes.Soft(), css=custom_css, title="Виділення прикметників") as demo:
    gr.HTML(
        """
        <div id="header-banner">
            <h1>Морфологічний аналізатор: виділення прикметників</h1>
            <p>Варіант 13 • Автоматичний пошук, підсвічування та граматичний розбір прикметників українського тексту</p>
        </div>
        """
    )

    with gr.Row():
        with gr.Column(scale=1):
            input_text = gr.Textbox(
                label="Вхідний текст українською мовою",
                placeholder="Введіть або вставте сюди речення чи абзац українською мовою (мінімум 3 символи)...",
                lines=8,
                info="Формат вводу: зв'язний текст українською мовою. Порожні рядки або текст без кирилиці відхиляються.",
            )
            with gr.Row():
                analyze_btn = gr.Button("Виділити прикметники", variant="primary")
                clear_btn = gr.ClearButton(components=[input_text], value="Очистити")

            gr.Examples(
                examples=[
                    [load_sample("test_1.txt") or "Теплий весняний вітер ніжно колихав молоді зелені листочки на високих деревах."],
                    [load_sample("test_2.txt") or "Сучасна комп'ютерна лінгвістика використовує складні математичні моделі та відкриті мовні корпуси."],
                    [load_sample("test_3.txt") or "На старовинній київській площі зібралися талановиті українські митці та молоді студенти."],
                ],
                inputs=input_text,
                label="Готові тестові тексти (натисніть, щоб підставити)",
            )

        with gr.Column(scale=1):
            highlighted_out = gr.HighlightedText(
                label="Текст із підсвіченими прикметниками",
                combine_adjacent=False,
                show_legend=True,
                color_map={"Прикметник": "#bbf7d0"},
            )
            summary_out = gr.Markdown("### Результати аналізу\nВведіть текст ліворуч і натисніть **«Виділити прикметники»**.")

    table_out = gr.Dataframe(
        headers=["№", "Словоформа", "Початкова форма (лема)", "Рід", "Число", "Відмінок"],
        datatype=["number", "str", "str", "str", "str", "str"],
        label="Детальний морфологічний розбір знайдених прикметників",
        interactive=False,
    )

    analyze_btn.click(
        fn=analyze_ui,
        inputs=input_text,
        outputs=[highlighted_out, summary_out, table_out],
    )

if __name__ == "__main__":
    demo.launch(share=True)
