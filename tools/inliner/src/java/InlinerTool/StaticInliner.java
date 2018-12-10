package InlinerTool;

import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;

import soot.Body;
import soot.PackManager;
import soot.PhaseOptions;
import soot.SceneTransformer;
import soot.Transform;

import soot.options.Options;

import soot.SootMethod;
import soot.SootClass;
import soot.Scene;
import soot.Unit;
import soot.Value;

import soot.jimple.InvokeExpr;
import soot.jimple.Stmt;

import soot.jimple.toolkits.invoke.InlinerSafetyManager;
import soot.jimple.toolkits.invoke.SiteInliner;


import soot.tagkit.Tag;
import soot.tagkit.BytecodeOffsetTag;

public class StaticInliner extends SceneTransformer {

	private HashMap<String, String> inlineCalls;
	private HashMap<String, SootMethod> methodMap;
	private HashMap<String, String> successfulInlines;
	
	public StaticInliner(String inlineOutput) {
		inlineCalls = new HashMap<>();
		methodMap = new HashMap<>();
		successfulInlines = new HashMap<>();

		try (FileReader fr = new FileReader(inlineOutput)) {
			BufferedReader br = new BufferedReader(fr);
			String line = null;
			while ((line = br.readLine()) != null) {
				String[] lineSplit = line.split(" ");
				inlineCalls.put(lineSplit[0].replace('/', '.'), lineSplit[1].replace('/', '.'));
			}
		} catch (IOException e) {
			System.out.println("Unable to open \"" + inlineOutput + "\"");
		}

	}

	@Override
	public void internalTransform(String phaseName, Map options) {
		HashMap<String, SootMethod> methodMap = new HashMap<>();
        	String modifierOptions = PhaseOptions.getString(options, "allowed-modifier-changes");


		//for (SootClass sc : Scene.v().getClasses()) {
		for (SootClass sc : Scene.v().getApplicationClasses()) {
			for (SootMethod m : sc.getMethods()) {
				String className = m.getDeclaringClass().getName();
				String methodName = m.getName();
				if (m.isConcrete()) {
					methodMap.put(className + "." + methodName, m);
				}
			}
		}

		for (Map.Entry<String, String> e : inlineCalls.entrySet()) {
			String callsite = e.getKey();
			String calleeMethodName = e.getValue();
			String[] callsiteSplit = callsite.split("@");
			String callsiteMethodName = callsiteSplit[0];
			int callsiteBci = Integer.parseInt(callsiteSplit[1]);
			
			if (!methodMap.containsKey(callsiteMethodName) || !methodMap.containsKey(calleeMethodName)) {
				continue;
			}
			
			SootMethod sootCallsite = methodMap.get(callsiteMethodName);
			SootMethod sootCallee = methodMap.get(calleeMethodName);
			if (sootCallsite.isJavaLibraryMethod()) {
				continue;
			}
			handleMethod(sootCallsite, sootCallee, callsiteBci, modifierOptions);
		}

		System.out.println("entry set =");
		System.out.println(successfulInlines.entrySet());
		System.out.println("end entry set");


	}

	private void handleMethod(SootMethod callsite, SootMethod callee, int callsiteBci, String options) {
		Body b = callsite.retrieveActiveBody();
		callee.retrieveActiveBody();
		Iterator units = b.getUnits().snapshotIterator();
		while (units.hasNext()) {
			Stmt stmt = (Stmt) units.next();
			if (stmt.containsInvokeExpr()) {
				InvokeExpr ie = stmt.getInvokeExpr();
				boolean hasNullArg = false;
				for (Value v : ie.getArgs()) {
					if (v == null) {
						hasNullArg = true;
					}
				}

				if (hasNullArg) {
					continue;
				}
				String className =  b.getMethod().getDeclaringClass().getName();
				String methodName =  b.getMethod().getName();
				BytecodeOffsetTag tag = (BytecodeOffsetTag) stmt.getTag("BytecodeOffsetTag");

				if (tag == null) {
					continue;
				}

				int bci = tag.getBytecodeOffset();

				if (callsiteBci == bci) {
					String qualifiedCallsiteMethodName = className + "." + methodName;
					String callsiteString = qualifiedCallsiteMethodName + "@" + bci;
					String calleeString = callee.getName();
					String qualifiedCalleeName = callee.getDeclaringClass().getName() + "." + calleeString;

					if (!qualifiedCallsiteMethodName.equals(qualifiedCalleeName)) {
						System.out.println("attempt " + callsiteString + " " + qualifiedCalleeName);
						if (callee == null || stmt == null || b == null || callsite  == null) {
							System.out.println("found a null");
							continue;
						}

						if (InlinerSafetyManager.ensureInlinability(callee, stmt, callsite, options)) {
							SiteInliner.inlineSite(callee, stmt, callsite);
							System.out.println("success on " + callsiteString + " " + qualifiedCalleeName);
							successfulInlines.put(callsiteString, calleeString);
						}
					}
				}
			}
		}

	}
}	
