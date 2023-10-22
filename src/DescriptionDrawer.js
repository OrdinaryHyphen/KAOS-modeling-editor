import React from 'react';
import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Drawer from '@material-ui/core/Drawer';
import DialogTitle from '@material-ui/core/DialogTitle';
import Divider from '@material-ui/core/Divider';
import Button from '@material-ui/core/Button';
import IconButton from '@material-ui/core/IconButton';
import AceEditor from 'react-ace';
import ChevronLeftIcon from '@material-ui/icons/ChevronLeft';
import ChevronRightIcon from '@material-ui/icons/ChevronRight';
import Toolbar from '@material-ui/core/Toolbar';


const drawerWidth = '100%';

const styles = theme => ({
  root: {
    flexGrow: 1,
  },
  hide: {
    display: 'none',
  },
  drawerPaper: {
    position: 'relative',
    width: drawerWidth,
    height: 'calc(100vh - 64px - 2 * 12px)',
    textAlign: 'left',
  },
  drawerHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'flex-end',
    padding: '0 8px',
    textTransform: 'capitalize',
    ...theme.mixins.toolbar,
  },
});


class DescriptionDrawer extends React.Component {

  handleChange = (value, event) => {
    this.props.onTextChange(value);
  };

  handleClick = () => {
    this.props.onClick();
  };

  handleDrawerClose = () => {
    this.props.onDescriptionDrawerClose();
  };

  startParsing = () => {
   this.props.onStartParsing();
  };

  render() {
    const { classes, theme } = this.props;

    return (
      <div className={classes.root}>
        <Drawer
          id="format-drawer"
          variant="persistent"
          anchor='left'
          open
          classes={{
            paper: classes.drawerPaper,
          }}
          onClick={this.handleClick}
        >
          <div className={classes.drawerHeader}>
            <DialogTitle id="form-dialog-title">
              Goal Descriptions
            </DialogTitle>
            <IconButton id="close-button" onClick={this.handleDrawerClose}>
              {theme.direction === 'rtl' ? <ChevronRightIcon /> : <ChevronLeftIcon />}
            </IconButton>
          </div>
          <Divider />
            <AceEditor
                mode="txt"
                theme="github"
                fontSize={this.props.fontSize + 'px'}
                tabSize={this.props.tabSize}
                value={this.props.goalDescription}
                height= '80%'
                width= '100%'
                wrapEnabled
                softWrap={false}
                setOptions={{
                 "indentedSoftWrap": false,
                }}
                onChange={this.handleChange}
             />
           <Divider />
           <Toolbar>
       <p>
         Input goal descriptions, then press the right button.
       </p>
       <div style={{flexGrow: 1}}></div>
      <Button
           color="inherit"
           size="Large"
           style={{flexGrow: 0.2}}
           onClick={this.startParsing}
        >
         Parse
        </Button>
        </Toolbar>
        </Drawer>
      </div>
    );
  }
}

DescriptionDrawer.propTypes = {
  classes: PropTypes.object.isRequired,
  theme: PropTypes.object.isRequired,
};

export default withStyles(styles, { withTheme: true })(DescriptionDrawer);