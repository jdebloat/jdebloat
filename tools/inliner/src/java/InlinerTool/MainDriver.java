package InlinerTool;
import soot.*;
import java.util.Arrays;
import java.util.ArrayList;
import java.util.List;

public class MainDriver {
	public static void main(String[] args) {
		if (args.length < 2) {
			//System.out.println("USAGE: java MainDriver (options) <classname> <inline output>");
			System.exit(1);
		}
		
		//Pack wjtp = PackManager.v().getPack("wjtp");
		//wjtp.add(new Transform("wjtp.instrumenter", new StaticInliner(args[args.length-1])));

		//soot.Main.main(Arrays.copyOfRange(args,0, args.length-1));

		String inlineTargetsPath = args[args.length-1];
		List<String> argsList = new ArrayList<String>(Arrays.asList(args));
		String removed = argsList.remove(argsList.size()-1);
		System.out.println("removed = " + removed);
		argsList.addAll(Arrays.asList(new String[] {"-pp",
				    "-keep-offset",
				    "-w"}));
		PackManager.v().getPack("wjtp").add(
		new Transform("wjtp.InlinerTool", new StaticInliner(inlineTargetsPath)));
		
		args = argsList.toArray(new String[0]);
		soot.Main.main(args);
	}
}
