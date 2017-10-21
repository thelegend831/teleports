﻿using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

public class GameMain : MonoBehaviour {

    private static GameMain instance;

    public Camera uiCamera;

    GameObject player;
    GameObject mainCanvas;

    float gameTime;
    float teleportTime;

    int score, startXp;

    bool endScreenOn;
    GameObject endScreen;

    bool isPaused;

    void Awake()
    {
        if (instance == null)
        {
            instance = this;
        }
        else if (instance != this)
        {
            Destroy(gameObject);
        }

        MenuController.Instance.CloseAll();

        SpawnPlayer();

        startXp = player.GetComponent<XpComponent>().Xp;
        mainCanvas = Instantiate(Resources.Load("Prefabs/UI/MainCanvas"), gameObject.transform) as GameObject;

        endScreenOn = false;
        isPaused = false;
        gameTime = 0;
    }

    
    void Start () {
        UnpauseGame();
        teleportTime = MainData.CurrentPlayerData.CurrentTeleportData.Time;
    }
	
	void Update () {

        gameTime += Time.deltaTime;

        if (gameTime >= teleportTime)
        {
            EndScreen("Time's up!");
        }

        if (!player.GetComponent<Unit>().Alive())
        {
            EndScreen("You died!");
        }

        score = player.GetComponent<XpComponent>().Xp - startXp;
                   
	}

    private void EndScreen(string text)
    {
        if (!endScreenOn)
        {
            PauseGame();
            endScreen = Instantiate(Resources.Load("Prefabs/UI/EndScreen"), mainCanvas.transform) as GameObject;
            endScreen.GetComponent<EndScreenUI>().SetText(text);
            endScreenOn = true;
        }
    }

    private void PauseGame()
    {
        isPaused = true;
    }

    private void UnpauseGame()
    {
        isPaused = false;
    }

    private void SpawnPlayer()
    {
        //try finding player object, if not found, spawn new one
        if(player != null) { return; }

        player = PlayerSpawner.Spawn(new PlayerSpawnerParams(gameObject, PlayerSpawnerParams.SpawnType.World));
       
    }

    public void BackToHome()
    {
        MainData.SavePlayer(player);
        MenuController.Instance.OpenMenu(MenuController.MenuType.ChooseCharacter);
        MainController.SwitchScene("Main");
    }

    public static GameMain Instance
    {
        get { return instance; }
    }

    public GameObject Player
    {
        get
        {
            if(player == null)
            {
                player = GameObject.FindGameObjectWithTag("Player");
                if(player == null)
                {
                    SpawnPlayer();
                }
            }
            return player;
        }
    }

    public bool IsPaused
    {
        get { return isPaused; }
    }

    static public float TimeLeft
    {
        get { return instance.teleportTime - instance.gameTime; }
    }

    public int Score
    {
        get { return score; }
    }
}
