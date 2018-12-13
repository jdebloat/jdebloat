package InlinerTool;

import soot.PackManager;
import soot.Transform;

import java.io.IOException;
import java.util.Arrays;
import java.util.ArrayList;
import java.util.List;

public class Main {
	public static void main(String[] args) throws IOException {
		if (args.length < 2) {
			System.exit(1);
		}
		
		String inlineTargetsPath = args[args.length - 1];
		List<String> argsList =
			new ArrayList<String>(Arrays.asList(args));
		String removed = argsList.remove(argsList.size() - 1);
		argsList.addAll(Arrays.asList(
			new String[] {"-pp", "-keep-offset", "-w"}));
		args = argsList.toArray(new String[0]);

		PackManager.v().getPack("wjtp").add(
			new Transform(
				"wjtp.InlinerTool",
				new InlinerTransformer(inlineTargetsPath)));
		soot.Main.main(args);
	}
}
