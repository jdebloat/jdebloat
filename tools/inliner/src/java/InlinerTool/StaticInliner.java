package InlinerTool;

import java.util.Map;
import java.util.HashMap;
import java.util.Iterator;
import java.io.File;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;

import soot.Body;
import soot.SceneTransformer;
import soot.PackManager;
import soot.Transform;
import soot.options.Options;

import soot.jimple.Stmt;
import soot.Unit;
import soot.SootMethod;
import soot.SootClass;
import soot.Scene;

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
				inlineCalls.put(lineSplit[0], lineSplit[1]);
			}
		} catch (IOException e) {
			System.out.println("Unable to open \"" + inlineOutput + "\"");
		}

	}

	@Override
	public void internalTransform(String phaseName, Map options) {
		HashMap<String, SootMethod> methodMap = new HashMap<>();

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
			handleMethod(sootCallsite.retrieveActiveBody(), sootCallee, callsiteBci);
		}

		System.out.println("entry set =");
		System.out.println(successfulInlines.entrySet());
		System.out.println("end entry set");


	}

	private void handleMethod(Body b, SootMethod callee, int callsiteBci) {
		callee.retrieveActiveBody();
		Iterator units = b.getUnits().snapshotIterator();
		while (units.hasNext()) {
			Stmt stmt = (Stmt) units.next();
			if (stmt.containsInvokeExpr()) {
				
				String className =  b.getMethod().getDeclaringClass().getName();
				String methodName =  b.getMethod().getName();
				int bci = -1;
				for (Tag t : stmt.getTags()) {
					if (t instanceof BytecodeOffsetTag) {
						bci = ((BytecodeOffsetTag)t).getBytecodeOffset();
					}
				}

				//System.out.println("Stmt: " + stmt + " bci=" + bci + " callsiteBci=" + callsiteBci);
				if (callsiteBci == bci) {
					String callsiteString = className + "." + methodName + "@" + bci;
					String calleeString = callee.getName();
					successfulInlines.put(callsiteString, calleeString);
					SiteInliner.inlineSite(callee, stmt, b.getMethod());
				} 
				//String callsite = className + "." + methodName + "@" + bci;
				
			
				//System.out.println("found: " + inlineCalls.get(callsite));
				//String callee = inlineCalls.get(callsite);
				// use callee string to look up site
					
				//SiteInliner.inlineSite(<>, stmt, b.getMethod());
				//if (toInline.getName().equals("b")) {
				//	SiteInliner.inlineSite(toInline, stmt, b.getMethod());
				//}
			}
		}

	}
}	
