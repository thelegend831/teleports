﻿using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;

//Main class
//Singleton
//Manages async Scene loading
//Acts as loading screen
public class MainController : MonoBehaviour {
    
    private static MainController mainController;
    
    private string currentSceneName = SceneNames.Main;
    private string nextSceneName;
    private AsyncOperation resourceUnloadTask;
    private AsyncOperation sceneLoadTask;
    private enum SceneState { Reset, Preload, Load, Unload, Postload, Ready, Run, Count };
    private SceneState sceneState;
    private delegate void UpdateDelegate();
    private UpdateDelegate[] updateDelegates;
    
    public string startSceneName = SceneNames.Home;
    public LoadingGraphics loadingGraphics;
    
    void Awake()
    {
        DontDestroyOnLoad(gameObject);
        
        mainController = this;
        
        updateDelegates = new UpdateDelegate[(int)SceneState.Count];
        
        updateDelegates[(int)SceneState.Reset] = UpdateSceneReset;
        updateDelegates[(int)SceneState.Preload] = UpdateScenePreload;
        updateDelegates[(int)SceneState.Load] = UpdateSceneLoad;
        updateDelegates[(int)SceneState.Unload] = UpdateSceneUnload;
        updateDelegates[(int)SceneState.Postload] = UpdateScenePostload;
        updateDelegates[(int)SceneState.Ready] = UpdateSceneReady;
        updateDelegates[(int)SceneState.Run] = UpdateSceneRun;

        nextSceneName = startSceneName;
        sceneState = SceneState.Run;
    }
    
    void Update()
    {
        if (updateDelegates[(int)sceneState] != null)
        {
            updateDelegates[(int)sceneState]();
        }
    }

    void OnDestroy()
    {
        if (updateDelegates != null)
        {
            for (int i = 0; i < updateDelegates.Length; i++)
            {
                updateDelegates[i] = null;
            }
            updateDelegates = null;
        }

        if (mainController != null)
        {
            mainController = null;
        }
    }

    void OnApplicationQuit()
    {
        MainData.SaveDataSO.Save();
    }

    public static void SwitchScene(string nextSceneName)
    {
        if (mainController != null)
        {
            if (mainController.currentSceneName != nextSceneName)
            {
                mainController.nextSceneName = nextSceneName;
            }
        }
    }
    
    private void UpdateSceneReset()
    {
        System.GC.Collect();
        sceneState = SceneState.Preload;
    }
    
    private void UpdateScenePreload()
    {
        loadingGraphics.SetActive(true);
        sceneLoadTask = SceneManager.LoadSceneAsync(nextSceneName);

        if(currentSceneName == "Main" && nextSceneName == "Home")
        {
            MainData.SaveDataSO.Load();
        }
        else if(currentSceneName == "World" && nextSceneName == "Home")
        {
            MainData.SaveDataSO.Save();
        }
        sceneState = SceneState.Load;
    }
    
    private void UpdateSceneLoad()
    {
        if (sceneLoadTask == null || sceneLoadTask.isDone)
        {
            sceneState = SceneState.Unload;
        }
        else
        {
            loadingGraphics.UpdateProgress(sceneLoadTask.progress);
        }
    }
    
    private void UpdateSceneUnload()
    {
        if(resourceUnloadTask == null)
        {
            resourceUnloadTask = Resources.UnloadUnusedAssets();
        }
        else
        {
            if (resourceUnloadTask.isDone)
            {
                resourceUnloadTask = null;
                sceneState = SceneState.Postload;
            }
        }
    }
    
    private void UpdateScenePostload()
    {
        loadingGraphics.SetActive(false);
        currentSceneName = nextSceneName;
        sceneState = SceneState.Ready;
    }
    
    private void UpdateSceneReady()
    {
        sceneState = SceneState.Run;
    }
    
    private void UpdateSceneRun()
    {
        if(currentSceneName != nextSceneName)
        {
            sceneState = SceneState.Reset;
        }
    }

}
