﻿using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Text = TMPro.TextMeshProUGUI;
using UnityEditor;
using Sirenix.OdinInspector;
using Sirenix.Serialization;

[ExecuteInEditMode]
[ShowOdinSerializedPropertiesInInspector]
[System.Serializable]
public class TextWidget : SerializedMonoBehaviour
{
    private Text text;

    [OdinSerialize]
    [ListDrawerSettings(Expanded = true)]
    private List<ITextWidgetStyle> styles = new List<ITextWidgetStyle>();

    void Awake()
    {
        if(text == null)
        {
            text = gameObject.AddComponent<Text>();
        }
    }

    [Button]
    void ApplyStyles()
    {
        foreach(var style in styles)
        {
            ApplyStyle(style);
        }
    }

    private void ApplyStyle(ITextWidgetStyle style)
    {
        text.font = style.Font ?? text.font;
        text.fontSize = style.FontSize ?? text.fontSize;
    }

    [MenuItem("GameObject/Widgets/Text", false, 10)]
    private static void Create(UnityEditor.MenuCommand command)
    {
        GameObject widget = new GameObject("Text Widget");
        widget.AddComponent<TextWidget>();
        widget.CreateFromEditor(command);
    }
}