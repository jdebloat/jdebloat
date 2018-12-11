package InlinerTool;

import soot.ArrayType;
import soot.Body;
import soot.BooleanType;
import soot.ByteType;
import soot.CharType;
import soot.DoubleType;
import soot.FloatType;
import soot.IntType;
import soot.LongType;
import soot.PackManager;
import soot.PrimType;
import soot.PhaseOptions;
import soot.RefType;
import soot.Scene;
import soot.SceneTransformer;
import soot.ShortType;
import soot.SootMethod;
import soot.SootClass;
import soot.Transform;
import soot.Type;
import soot.Unit;
import soot.Value;
import soot.jimple.InvokeExpr;
import soot.jimple.Stmt;
import soot.jimple.toolkits.invoke.InlinerSafetyManager;
import soot.jimple.toolkits.invoke.SiteInliner;
import soot.options.Options;
import soot.tagkit.Tag;
import soot.tagkit.BytecodeOffsetTag;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.lang.RuntimeException;
import java.lang.StringBuilder;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;

public class InlinerTransformer extends SceneTransformer {

	private HashMap<String, HashMap<Integer, String>> inlineTargets = new HashMap<>();
	private HashMap<String, SootMethod> methodMap = new HashMap<>();
	
	public InlinerTransformer(String inlineTargetsPath) throws IOException {
		FileReader fileReader = new FileReader(inlineTargetsPath);
		BufferedReader bufferedReader = new BufferedReader(fileReader);
		String line = null;
		while ((line = bufferedReader.readLine()) != null) {
			String[] lineSplit = line.split(" ");
			String callsiteSignature = lineSplit[0];
			String calleeHotSpotSignature = lineSplit[1];

			String[] callsiteSignatureSplit =
				callsiteSignature.split("@");
			String callerHotSpotSignature =
				callsiteSignatureSplit[0];
			Integer callsiteBytecodeOffset =
				Integer.valueOf(callsiteSignatureSplit[1]);

			if (!inlineTargets.containsKey(callerHotSpotSignature)) {
				inlineTargets.put(callerHotSpotSignature, new HashMap<>());
			}
			inlineTargets.get(callerHotSpotSignature)
			             .put(callsiteBytecodeOffset, calleeHotSpotSignature);
		}
	}

	// https://docs.oracle.com/javase/specs/jvms/se8/html/jvms-4.html#jvms-4.3.2
	private void buildFieldDescriptor(StringBuilder sb, Type type) {
		if (type instanceof RefType) {
			RefType refType = (RefType) type;
			String sootClassName = refType.getClassName();
			sb.append('L');
			sb.append(sootClassName.replace('.', '/'));
			sb.append(';');
		}
		else if (type instanceof ArrayType) {
			ArrayType arrayType = (ArrayType) type;
			sb.append('[');
			buildFieldDescriptor(sb, arrayType.baseType);
		}
		else if (type instanceof BooleanType) {
			sb.append('Z');
		}
		else if (type instanceof ByteType) {
			sb.append('B');
		}
		else if (type instanceof CharType) {
			sb.append('C');
		}
		else if (type instanceof DoubleType) {
			sb.append('D');
		}
		else if (type instanceof FloatType) {
			sb.append('F');
		}
		else if (type instanceof IntType) {
			sb.append('I');
		}
		else if (type instanceof LongType) {
			sb.append('J');
		}
		else if (type instanceof ShortType) {
			sb.append('S');
		}
		else {
			throw new RuntimeException(
				"Unhandled Type: " + type.getClass().getName());
		}
	}

	private String getHotSpotSignature(SootMethod sootMethod) {
		SootClass sootClass = sootMethod.getDeclaringClass();
		StringBuilder sb = new StringBuilder();
		sb.append(sootClass.getName().replace('.', '/'));
		sb.append('.');
		sb.append(sootMethod.getName());
		sb.append('(');
		boolean firstParameter = true;
		for (Type parameterType : sootMethod.getParameterTypes()) {
			if (firstParameter) { firstParameter = false; }
			else                { sb.append(','); }

			if (parameterType instanceof RefType) {
				RefType refType = (RefType) parameterType;
				String sootClassName = refType.getClassName();
				sb.append(sootClassName.replace('.', '/'));
			}
			else if (parameterType instanceof PrimType) {
				PrimType primType = (PrimType) parameterType;
				sb.append(primType.toString());
			}
			else if (parameterType instanceof ArrayType) {
				buildFieldDescriptor(sb, parameterType);
			}
			else {
				throw new RuntimeException(
					"Unhandled Parameter Type: "
					+ parameterType.getClass().getName());
			}
		}
		sb.append(')');
		return sb.toString();
	}

	@Override
	public void internalTransform(String phaseName, Map options) {
		for (SootClass sootClass : Scene.v().getClasses()) {
			for (SootMethod sootMethod : sootClass.getMethods()) {
				if (!sootMethod.isConcrete()) {
					continue;
				}
				String hotSpotSignature =
					getHotSpotSignature(sootMethod);
				methodMap.put(hotSpotSignature, sootMethod);
			}
		}

		int count = 0;
		for (Map.Entry<String, HashMap<Integer, String>> entry
		     : inlineTargets.entrySet()) {
			String callerHotSpotSignature = entry.getKey();
			HashMap<Integer, String> bytecodeOffsetCalleeMap =
				entry.getValue();

			if (!methodMap.containsKey(callerHotSpotSignature)) {
				continue;
			}

			SootMethod sootCaller = methodMap.get(
				callerHotSpotSignature);
			handleInline(sootCaller, bytecodeOffsetCalleeMap);
		}
	}

	private void handleInline(SootMethod sootCaller,
	                          HashMap<Integer, String> bytecodeOffsetCalleeMap) {
		Body body = sootCaller.retrieveActiveBody();
		Iterator unitsIter = body.getUnits().snapshotIterator();
		while (unitsIter.hasNext()) {
			Stmt stmt = (Stmt) unitsIter.next();

			if (!stmt.containsInvokeExpr()) {
				continue;
			}
			InvokeExpr invokeExpr = stmt.getInvokeExpr();

			BytecodeOffsetTag bytecodeOffsetTag =
				(BytecodeOffsetTag)
				stmt.getTag("BytecodeOffsetTag");
			if (bytecodeOffsetTag == null) {
				continue;
			}
			int bytecodeOffset = bytecodeOffsetTag.getBytecodeOffset();
			Integer bytecodeOffsetKey = Integer.valueOf(bytecodeOffset);
			if (!bytecodeOffsetCalleeMap.containsKey(bytecodeOffsetKey)) {
				continue;
			}
			String calleeHotSpotSignature = bytecodeOffsetCalleeMap.get(bytecodeOffsetKey);
			if (!methodMap.containsKey(calleeHotSpotSignature)) {
			    continue;
			}
			SootMethod sootCallee = methodMap.get(calleeHotSpotSignature);
			sootCallee.retrieveActiveBody();

			boolean safeToInline =
				InlinerSafetyManager.ensureInlinability(
					sootCallee, stmt, sootCaller, "unsafe");
			if (!safeToInline) {
				continue;
			}
			SiteInliner.inlineSite(sootCallee, stmt, sootCaller);
		}
	}
}	
