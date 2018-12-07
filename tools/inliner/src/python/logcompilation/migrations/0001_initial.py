# Generated by Django 2.1.2 on 2018-12-07 02:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Callsite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bci', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='CompileThread',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='InlineCall',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='InvokeVirtualTerminator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=200)),
                ('reason', models.CharField(blank=True, max_length=200)),
                ('callsite', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='logcompilation.Callsite')),
                ('compile_thread', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='logcompilation.CompileThread')),
            ],
        ),
        migrations.CreateModel(
            name='Klass',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Method',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('klass', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='logcompilation.Klass')),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.AddField(
            model_name='log',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='logcompilation.Project'),
        ),
        migrations.AddField(
            model_name='inlinecall',
            name='callee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='logcompilation.Method'),
        ),
        migrations.AddField(
            model_name='inlinecall',
            name='caller',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='logcompilation.Callsite'),
        ),
        migrations.AddField(
            model_name='inlinecall',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='logcompilation.Project'),
        ),
        migrations.AddField(
            model_name='compilethread',
            name='log',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='logcompilation.Log'),
        ),
        migrations.AddField(
            model_name='callsite',
            name='caller',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='logcompilation.Method'),
        ),
    ]
