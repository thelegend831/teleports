﻿using System.Collections;
using System.Collections.Generic;
using Sirenix.Utilities;
using UnityEngine;

public class PlayerController : UnitController {
	
	// Update is called once per frame
	public override void Control () {
        if (Input.GetButton("PlayerMove"))
        {
            Ray ray = Camera.main.ScreenPointToRay(Input.mousePosition);
            RaycastHit hit;
            bool done = false;

            int enemyMask = (int)MyLayerMask.Enemy;
            int groundMask = (int)MyLayerMask.Ground;
            if (Input.GetButtonDown("PlayerMove") && Physics.Raycast(ray, out hit, Mathf.Infinity, enemyMask))
            {
                OnEnemyClick(hit.transform.gameObject.GetComponent<Unit>());
                done = true;
            }
            else if (!done && Physics.Raycast(ray, out hit, Mathf.Infinity, groundMask))
            {
                if (Input.GetButtonDown("PlayerMove")) OnGroundClicked(hit.point);
                else OnGroundPressed(hit.point);
            }
        }
	    if (Input.GetButtonDown("PlayerAutotarget"))
	    {
            TargetNearest();
	    }

        if (target.TargetUnit != null)
        {
            if (!target.TargetUnit.Alive || !unit.Alive) target.TargetUnit = null;
            else
            {
                //Debug.Log("Chasing");
                Chase();
            }
        }
    }

    protected void TargetNearest()
    {
        Collider[] enemyColliders =
            Physics.OverlapSphere(unit.transform.position, unit.ViewRange, (int) MyLayerMask.Enemy);
        if (enemyColliders.IsNullOrEmpty()) return;

        Collider closestCollider = enemyColliders[0];
        float minDistance = Mathf.Infinity;
        foreach (var collider in enemyColliders)
        {
            float distance = (collider.transform.position - unit.transform.position).magnitude;
            if (distance < minDistance)
            {
                closestCollider = collider;
                minDistance = distance;
            }
        }

        target.TargetUnit = closestCollider.gameObject.GetComponent<Unit>();
    }

    void OnEnemyClick(Unit enemy)
    {
        target.TargetUnit = enemy;
    }  

    void OnGroundPressed(Vector3 point)
    {
        unit.MovingState.Start(point);
    }

    void OnGroundClicked(Vector3 point)
    {
        target.TargetUnit = null;
        CastingState.TryStartResult tryStartResult = unit.CastingState.TryInterrupt();
        //Debug.Log("Ground Clicked - TryStartResult :" + tryStartResult.ToString());
        unit.MovingState.Start(point);
    }
}
